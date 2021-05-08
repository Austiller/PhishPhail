import numpy
from modeler.model import Fqdn
from os import walk, path
import math
import re
from collections import Counter, OrderedDict
#from stringdist import levenshtein
from Levenshtein import distance
import tldextract
import numpy as np


from psycopg2 import sql
import numpy
from collections import OrderedDict, defaultdict
import logging

from pandas import DataFrame
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import confusion_matrix
from datetime import datetime
from collections import OrderedDict, Counter
import pickle

from trainer.models import FQDN, Brand, TopLevelDomain, SquatedWord, KeyWord

from modeler.model import Fqdn

class Trainer:
    """
    Handles the training and packaging of the model, saving the model and attributes to the database. 

    Attributes:
        attributeManager (object):
        fqdnList (list): A list of Fqdn generated from from the FQDNs in the database marked for training.
        trainingAttributes (dict): 

    """
    def __init__(self,model_id,name):
        """
        Initializes the Trainer class, training the model, measuring the model and packaging the model. 
        
        """
        self.model_id = model_id
        self.name = name
        self.attributeManager = AttributeManager()
        self.fqdnList = [Fqdn(f.fqdn,f.fqdn_type) for f in FQDN.objects.all()]
        self.trainingAttributes = self.attributeManager.compute_attributes(self.fqdnList)
        self.modelDetails = {}
     

        self.train_model()
        self.measure_model()
        

        self.package_model()
    
    
    def __str__ (self):
        return self.modelDetails

    def __unicode__ (self):
        return self.modelDetails

    #Convert to class method

    def train_model (self):
        """
        Train the model with the attributes and labels generated from training set.

        Args:
            features (dictionary): Two keys - names and values, where names holds the feature
                vector and values holds the features from each FQDN from training.
            labels_list (list): Labels for training data (0 = benign, 1 = phishing).
        """
      
        
        #convert list of fqdns to numpy array 
        self.fqdnArr = numpy.fromiter( [fqdn.get_type_as_int() for fqdn in self.fqdnList], dtype=numpy.float) 
         
        
        # construct a dataframe of the attributes and normalized values
        attributeDf = DataFrame.from_records(self.trainingAttributes['values'], columns=self.trainingAttributes['names'])
        self.attributeVectors = self.trainingAttributes['names']


        #Split training data from data that's used to evaluate the model. 
        self._x_train, self._x_test, self._y_train, self._y_test = train_test_split(
            attributeDf.values, self.fqdnArr, random_state=2)

        #train the model
        self.model = LogisticRegression(C=10).fit(self._x_train, self._y_train)
        


        
    def measure_model (self):
        """
        Calculate metrics from the new model, required to evaluate model performance. 
          
            info
                algorithm, parameters, date/time, training set makeup
            performance
                training speed, analysis speed

        Args:
            None, stores details in class attribute modelDetails
        """
     


        # Get model info
        
        self.modelDetails['model_name'] = self.name
        self.modelDetails['model_algorithm'] = str(self.model).split('(')[0]


        self.modelDetails['model_benign_count'] = numpy.count_nonzero(self.fqdnArr == 0)
        self.modelDetails['model_malicious_count'] = numpy.count_nonzero(self.fqdnArr == 1)
       

        #Estimate model accuracy
    
        self.modelDetails['accuracy_training_set'] = "{:.5f}".format(self.model.score(
            self._x_train, self._y_train))
        self.modelDetails['accuracy_test_set'] = "{:.5f}".format(self.model.score(
            self._x_test, self._y_test))

        precision, recall, thresholds =  precision_recall_curve(self._y_test, self.model.predict_proba(self._x_test)[:, 1])
        close_zero = numpy.argmin(numpy.abs(thresholds - 0.5))
        self.modelDetails['accuracy_precision'] = "{:.4f}".format(precision[close_zero])
        self.modelDetails['accuracy_recall'] = "{:.4f}".format(recall[close_zero])

        # Accuracy - confusion matrix.
        predictions = self.model.predict_proba(self._x_test)[:, 1] > 0.5
        confusion = confusion_matrix(self._y_test, predictions)
        self.modelDetails['accuracy_confusion_matrix'] =  confusion.tolist()

        return self.modelDetails
        
        
        


    def package_model (self):
   
        from trainer.models import Model as trainerModel

        m = trainerModel(
            id = self.model_id,
            model_name=self.modelDetails['model_name'],
            model_algorithm=self.modelDetails['model_algorithm'],
            model_benign_count=  self.modelDetails['model_benign_count'],
            model_malicious_count= self.modelDetails['model_malicious_count'],
            accuracy_training_set= self.modelDetails['accuracy_training_set'],
            accuracy_test_set= self.modelDetails['accuracy_test_set'],
            accuracy_precision=    self.modelDetails['accuracy_precision'],
            accuracy_recall= self.modelDetails['accuracy_recall'],
            model_binary=  (pickle.dumps(self.model)),
            model_attributes =  (pickle.dumps(self.attributeManager))
    
            )

        try:
            # save the model
            m.save()
        except Exception as e:
            raise e
        
       
    
   


class AttributeManager:

    """ 

    __init__ (method): Loads the relevant training data points
    
    """

    def __init__(self):
        self.trainer_brand = {b.id:b.brand_name for b in Brand.objects.all()}
        self.trainer_topleveldomain = [t.tld  for t in TopLevelDomain.objects.all()]
        self.trainer_keyword = {kw.id:kw.keyword for kw in KeyWord.objects.all()}
        self.trainer_squatedword = [sw.squated_word for sw in SquatedWord.objects.all()]
      
     
        
    def compute_attributes (self,fqdnList,speed=False):

 
        result = {}
        attributes = []

       
        for fqdn in fqdnList:

            analysis = OrderedDict()
            for item in dir(self):
                
                if item.startswith('att_'):
                    analysisType = getattr(self,item)
                    result = analysisType(fqdn)
                    analysis = {**analysis, **result}
                   
            # Must sort dictionary by key before adding.
            analysis = OrderedDict(sorted(analysis.items()))
            attributes.append(analysis)    

        result = {}
        result['values'] = []
        for attribute in attributes:
            result['values'].append(numpy.fromiter(attribute.values(), dtype=float))

        
        if not speed:
            # Take the dictionary keys from the first item - this is the feature vector.
            result['names'] = attributes[0].keys()
        
        
        return result

    
    def att_brand (self,fqdn):

        """

        Checks the domain and subdomain for the precense of a monitored brand

        Args:
            fqdn (Fqdn): Fqdn Object

        Returns:
            result (OrderedDict): Keys are brand related names, values are attribute scores
        """
    
            
        results = OrderedDict()
        # Brand is a dict containing the brand_id and brand_name.
        try:
            for brand_id,brand in self.trainer_brand.items():
                results["{}_brand_dn".format(brand)] = 0
                results["{}_brand_sn".format(brand)] = 0

                if (brand in fqdn.words):
                    results["{}_brand_dn".format(brand)] = 1
                    fqdn.brand_match[brand] = brand_id
                if(brand == fqdn.subdomain):
                    results["{}_brand_sn".format(brand)] = 1
                    fqdn.brand_match[brand] = brand_id


        except Exception as e:
            raise Exception("att_brand")

        return results

    def att_number_check (self, fqdn):
        
        """

        Check to see if the fqdn starts with a number

        Args:
            fqdn (Fqdn): Fqdn Object

        Returns:
            result (OrderedDict): Keys are tld related names, values are attribute scores
        """

        results = OrderedDict()

        regCheck = re.compile("[A-z]*[0-9]{1,}[A-z]+")
        
        results['num_start'] = 1 if regCheck.search(fqdn.fqdn) != None else 0

     

        return results

    def att_topleveldomain (self,fqdn):

        """
        Check if fqdn tld is in a list of tracked tlds indicative of phishing 

        Args:
            fqdn (Fqdn): Fqdn Object

        Returns:
            result (OrderedDict): Keys are tld related names, values are attribute scores
        """

        results = OrderedDict()
        #trainer_topleveldomain is a dict with tld_id as the key and tld as the value
        for tld in self.trainer_topleveldomain:
            results["tld_{}".format(tld)] = 1 if (tld == fqdn.tld) else 0

        return results
    
    def att_keyword (self,fqdn):

        """
        Check if fqdn or any of its components contain one or more of the montired keywords indicative of phishing 

        Args:
            fqdn (Fqdn): Fqdn Object

        Returns:
            result (OrderedDict): Keys are kekyword related names, values are attribute scores
        """

        results = OrderedDict()

        for kw_id,kw in self.trainer_keyword.items():
            results["{}_kw".format(kw)] = 0
            results["{}_kw_fqdn_word".format(kw)] = 0

            if (kw in fqdn.fqdn):
                results["{}_kw".format(kw)] = 1
                fqdn.keyword_match[kw] = kw_id
            if(kw in fqdn.words):
                results["{}_kw_fqdn_word".format(kw)] = 1
                fqdn.keyword_match[kw] = kw_id

    
        
        return results

    
    
    def att_compute_randomness(self,fqdn):
        """
        Takes domain name from FQDN and compute domain randomness.

        Args:
            fqdn (Fqdn): fqdn Object

        Returns:
            result (dictionary): Keys are attribute labels, values are attribute scores
        """
        # Compute entropy of domain.
        result = OrderedDict()

        #returns the length of the domain and the count of each character in the domain. 
        p, lngth = Counter(fqdn.domain), float(len(fqdn.domain))

        #Maybe Improve by calculating the entropy of the fully FQDN and domain, possibly the fqdn-words as well. 

        fqdn.entropy = -sum(count / lngth * math.log(count / lngth, 2) for count in list(p.values()))
        result['entropy'] = fqdn.entropy
        return result
       
    def att_count_dashes(self,fqdn):
        """
        count the number of dashes in the FQDN with multiple dashes indicating the FQDN is more likely to be associated with phishing. 

        Args:
            fqdn (Fqdn): Fqdn Object

        Returns:
            result (dictionary): Keys are attribute labels, values are attribute scores
        """
        result = OrderedDict()

        
        dashCount = fqdn.fqdn.count("-")
    
        result['dashes'] = 0 if dashCount > 2 else dashCount
       
        return result
    
    def att_count_repeating_characters(self,fqdn):
        """
        Count the number of characters that repeat more than 3 times in a row. 

        args:
            fqdn(Fqdn): Fqdn object

        returns:
            result (dictionary): Keys are 
    
        """
        result = OrderedDict()
        charCount = defaultdict(int)
        for c in fqdn.fqdn:
            charCount[c] += 1
    
            
        result['repeatChars'] = len( [char for char in charCount.values() if char > 2])
        return result


    def att_count_periods(self,fqdn):
        """
        count the number of dashes in the FQDN with multiple dashes indicating the FQDN is more likely to be associated with phishing. 

        Args:
            fqdn (Fqdn): Fqdn Object

        Returns:
            result (dictionary): Keys are attribute labels, values are attribute scores
        """
        result = OrderedDict()
        result['periods'] = fqdn.fqdn.count(".")
        return result


    def att_squated_words (self,fqdn):
        """
            Measures the  the similarity between words commonly associated with phishing and those found in the 
            FQDN. Looks for a max distance of 1

            a distance of 1 would for the word 'WellsFargo' would look like 'W3llsFargo', 'We1lsFargo'

        

        Args:
            fqdn (Fqdn):  Fqdn Object

        Returns:
            result (dictionary): Keys are attribute labels, values are attribute scores
        """
        result = OrderedDict()
       # Can use this library if C++ Not installed. 
       # from difflib import SequenceMatcher

        for sw in self.trainer_squatedword:
            result[sw + "_lev_1"] = 0
 
            for word in fqdn.words:
                dist = distance(word,sw)
                if dist == 1:
                    result[sw + "_lev_1"] = 1

        return result

    def att_squated_brand (self,fqdn):
        """
        Takes the list of fqdn words and checks the similarity in comparison to a list of brand names. 
        
        Searches for a maximum distance of 2
    
        for example:
            a distance of 1 would for the word 'WellsFargo' would look like 'W3llsFargo', 'We1lsFargo'

            A distance of 2 for a word like 'WellsFargo' would look like 'We11sFargo' or 'Wel15Fargo'

        Args:
            fqdn (Fqdn):  Fqdn Object

        Returns:
            result (dictionary): Keys are attribute labels, values are attribute scores
        """
        result = OrderedDict()
       # Can use this library if C++ Not installed. 
       # from difflib import SequenceMatcher

        for brand_id,brand in self.trainer_brand.items():
            result[brand + "_brand_lvl_1"] = 0
            result[brand + "_brand_lvl_2"] = 0

            for word in fqdn.words:
                dist = distance(word,brand)
                if dist == 1 and len(word) > 5:
                    result[brand + "_brand_lvl_1"] = 2
                    fqdn.brand_match[brand] = brand_id 

                elif (dist == 2 and len(brand) > 5):
                    result[brand + "_brand_lvl_2"] = 2
                    fqdn.brand_match[brand] = brand_id


        return result
