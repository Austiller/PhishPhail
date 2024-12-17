import psycopg2
import math
import re
import logging
import tldextract
import pickle
import numpy as np
from collections import Counter, OrderedDict, defaultdict
from pandas import DataFrame
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    precision_recall_curve, 
    confusion_matrix
)

DB_CONFIG = {
    "dbname": "your_db_name",
    "user": "your_db_user",
    "password": "your_db_password",
    "host": "localhost",
    "port": 5432
}

class AttributeManager:
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()
        self.trainer_brand = self.fetch_data("SELECT brand_name FROM brand_table;")
        self.trainer_topleveldomain = self.fetch_data("SELECT tld FROM topleveldomain_table;")
        self.trainer_keyword = self.fetch_data("SELECT keyword FROM keyword_table;")
        self.trainer_squatedword = self.fetch_data("SELECT squated_word FROM squatedword_table;")

    def fetch_data(self, query):
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]

    def compute_attributes(self, fqdnList):
        attributes = []
        for fqdn in fqdnList:
            analysis = OrderedDict()
            analysis.update(self.att_brand(fqdn))
            analysis.update(self.att_number_check(fqdn))
            analysis.update(self.att_topleveldomain(fqdn))
            attributes.append(OrderedDict(sorted(analysis.items())))
        return {'values': [list(attr.values()) for attr in attributes], 
                'names': list(attributes[0].keys())}

    def att_brand(self, fqdn):
        results = OrderedDict()
        for brand in self.trainer_brand:
            results[f"{brand}_brand"] = 1 if brand in fqdn.fqdn else 0
        return results

    def att_number_check(self, fqdn):
        regCheck = re.compile(r"([0-9]+[A-z]*|[A-z]*[0-9]+)")
        return {'num_start': 1 if regCheck.search(fqdn.fqdn) else 0}

    def att_topleveldomain(self, fqdn):
        return {'tld_match': 1 if fqdn.tld in self.trainer_topleveldomain else 0}


class Trainer:
    def __init__(self, model_id: int):
        self.model_id = model_id
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()
        self.attributeManager = AttributeManager(self.conn)
        
        # Fetch training data
        self.fqdnList = self.fetch_fqdns()
        self.trainingAttributes = self.attributeManager.compute_attributes(self.fqdnList)
        self.modelDetails = {}

        self.train_model()
        self.measure_model()
        self.package_model()

    def fetch_fqdns(self):
        """Fetch FQDN data from the database."""
        query = "SELECT fqdn, fqdn_type FROM fqdn_table;"
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        
        # Convert fetched records to FQDN objects
        return [Fqdn.from_training_set(fqdn, fqdn_type) for fqdn, fqdn_type in records]

    def train_model(self):
        """Train the logistic regression model."""
        self.fqdnArr = np.array([fqdn.get_type_as_int() for fqdn in self.fqdnList], dtype=float)

        # Convert attributes to DataFrame
        attributeDf = DataFrame.from_records(self.trainingAttributes['values'], 
                                             columns=self.trainingAttributes['names'])
        self._x_train, self._x_test, self._y_train, self._y_test = train_test_split(
            attributeDf.values, self.fqdnArr, random_state=2
        )
        
        # Train the model
        self.model = LogisticRegression(C=12, max_iter=150, solver="sag").fit(self._x_train, self._y_train)

    def measure_model(self):
        """Evaluate model performance."""
        self.modelDetails['accuracy_training_set'] = "{:.5f}".format(self.model.score(self._x_train, self._y_train))
        self.modelDetails['accuracy_test_set'] = "{:.5f}".format(self.model.score(self._x_test, self._y_test))
        
        precision, recall, thresholds = precision_recall_curve(
            self._y_test, self.model.predict_proba(self._x_test)[:, 1]
        )
        close_zero = np.argmin(np.abs(thresholds - 0.5))
        self.modelDetails['accuracy_precision'] = "{:.4f}".format(precision[close_zero])
        self.modelDetails['accuracy_recall'] = "{:.4f}".format(recall[close_zero])

        predictions = self.model.predict_proba(self._x_test)[:, 1] > 0.5
        confusion = confusion_matrix(self._y_test, predictions)
        self.modelDetails['accuracy_confusion_matrix'] = confusion.tolist()

    def package_model(self):
        """Save the trained model and attributes to the database."""
        query = """
            UPDATE trainer_model
            SET model_algorithm = %s,
                model_benign_count = %s,
                model_malicious_count = %s,
                accuracy_training_set = %s,
                accuracy_test_set = %s,
                accuracy_precision = %s,
                accuracy_recall = %s,
                model_binary = %s
            WHERE id = %s;
        """
        self.cursor.execute(query, (
            "LogisticRegression",
            np.count_nonzero(self.fqdnArr == 0),
            np.count_nonzero(self.fqdnArr == 1),
            self.modelDetails['accuracy_training_set'],
            self.modelDetails['accuracy_test_set'],
            self.modelDetails['accuracy_precision'],
            self.modelDetails['accuracy_recall'],
            pickle.dumps(self.model),
            self.model_id
        ))
        self.conn.commit()
        print("Model and metrics saved successfully.")
      
      def load_model(self):
        """Load the trained model from the database."""
        query = "SELECT model_binary FROM trainer_model WHERE id = %s;"
        self.cursor.execute(query, (self.model_id,))
        result = self.cursor.fetchone()
        if result:
            self.model = pickle.loads(result[0])
            print("Model loaded successfully.")
        else:
            raise Exception("Model not found in the database.")
          
    def __del__(self):
        """Close database connection."""
        self.cursor.close()
        self.conn.close()

def predict_fqdns(trainer, sample_fqdns):
    """
    Predict the class (malicious/benign) for a list of sample FQDNs.

    Args:
        trainer (Trainer): Instance of the Trainer class.
        sample_fqdns (list): List of FQDN strings to classify.

    Returns:
        list: Predictions for the sample FQDNs.
    """
    # Convert sample FQDNs into Fqdn objects
    fqdn_objects = [Fqdn(fqdn) for fqdn in sample_fqdns]
    
    # Extract features using the same AttributeManager
    attributes = trainer.attributeManager.compute_attributes(fqdn_objects)
    feature_matrix = np.array(attributes['values'])

    # Use the loaded model to predict probabilities
    predictions = trainer.model.predict_proba(feature_matrix)[:, 1]

    # Convert probabilities into class predictions (0 or 1)
    result = ["Malicious" if prob > 0.5 else "Benign" for prob in predictions]
    return result

def run_model(model_id:int):
  # Initialize Trainer with the model ID
  model_id = 1  # Use the correct ID for your saved model
  trainer = Trainer(model_id)
  
  # Load the model from the database
  trainer.load_model()
  
  # Example list of FQDNs to classify
  sample_fqdns = [
      "secure-login.paypal.com",
      "update-w3lls.xyz",
      "safe-banking.com",
      "goog1e.com"
  ]
  
  # Run predictions
  predictions = predict_fqdns(trainer, sample_fqdns)
  
  # Print results
  for fqdn, prediction in zip(sample_fqdns, predictions):
      print(f"{fqdn}: {prediction}")

if __name__ == "__main__":
    model_id = 1  # Example model ID
    trainer = Trainer(model_id)
    
