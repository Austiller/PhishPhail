from os import walk, path
import math
import re
from collections import Counter, OrderedDict
#from stringdist import levenshtein
from Levenshtein import distance
import tldextract
import numpy as np
#from certStream.database import Database,Fqdn
from psycopg2 import sql
import numpy
from collections import OrderedDict, defaultdict
import certstream
from certstream.core import CertStreamClient
import logging
import pickle
from datetime import time
from trainer.models import FQDN, Brand, TopLevelDomain, KeyWord, SquatedWord, Model, FQDNInstance

from modeler.models import FoundFQDN
from background_task import background



class Fqdn:
    """
    Represents an FQDN seen by the cert stream


    args:
        fqdn (str)
    
    """

    def __init__(self,fqdn,fqdn_type='Unknown',issuing_ca=None,root_ca=None,cert_seen=None,subdomain=None,domain=None,tld=None,score=None):
        self.fqdn_full = fqdn
        self.fqdn = self.clean_fqdn(fqdn)
        self.fqdn_type = fqdn_type
        self.keyword_match = {}
        self.brand_match = {}
        self.squatedWords = {}
        self.issuingCA = None
        self.rootCA= None
        self.dateSeen = None
        self.fqdnParts =  tldextract.extract(fqdn)
        self.words =  re.split('\W+', fqdn)
        self.subdomain =  self.fqdnParts.subdomain
        self.domain = self.fqdnParts.domain
        self.tld = self.fqdnParts.suffix
        self.score = score

    def get_type_as_int (self)-> int: 
        if(self.fqdn_type.startswith('m')):
            return 1
        else:
            return 0
        
    def clean_fqdn (self,fqdn)-> str: 
        """ 
        Takes the provided FQDN and removes common subdomains.

        args:
            self
        
        returns:
            None
        
        """
    
        common_prefixes = ["*", "www", "mail", "cpanel", "webmail",
                        "webdisk", "autodiscover"]
        
        split_fqdn = fqdn.split(".",1)
        if len(split_fqdn ) > 1:
            if(split_fqdn[0] in common_prefixes):
                return split_fqdn[1]

        return fqdn

    def __str__ (self):

        return self.fqdn_full

       
class Modeler:
    """
   
    A class responsible for executing the found FQDNs via certstream. Starts the selected
    
        args:
            attributes (Dict): Represents the model attributes
            model (LinearRegression): The actual model itself
        
        methods:
            __init__,  start_using_default 


    """


    def __init__(self,attributes,model):
        self.attributes = attributes
        self.model = model
        
        


  
    def start(cls,model_id):
        return cls()

    def __call__ (self):
        """Start the listener"""
        #print("CertStream")
        certstream.listen_for_events(message_callback=self.certstream_handler, url='wss://certstream.calidog.io/')


    def certstream_handler (self,message, context):
        # May remove, set cerstream flag instead to ignore heartbeats
        if message['message_type'] == "heartbeat":
            return
        
        #Removes wildcard certs and www.* certs
        if message['message_type'] == "certificate_update":
            csFqdnList = message['data']['leaf_cert']['all_domains']
        
            
            

            for csFqdn in csFqdnList:
                if csFqdn.startswith('*.') and (csFqdn[2:] in csFqdnList):
                    csFqdnList.remove(csFqdn)

                elif csFqdn.startswith("www.") and (csFqdn[4:] in csFqdnList):
                    csFqdnList.remove(csFqdn)

          
               
            # 'Convert' found domains to a list Fqdn class. This will make updating the FQDNInstance table easier with the FQDN properties. 
            csFqdnList = [Fqdn(csFqdn,fqdn_type='unknown') for csFqdn in csFqdnList]

  
            try:

                scores = self.execute_model(csFqdnList)
                
            except Exception as error:
                
                # Write to system.log, assign prediction score of 0, continue.
                logging.error("{}: {}".format(error, message))
                scores = ([0] * len(csFqdnList))
               
            for csFqdn,score in zip(csFqdnList,scores):
                #update database. 

                csFqdn.score = score

                print("FQDN:{}\nScore:{}\nBrands:{}\nKeyWord:{}".format(csFqdn.fqdn,score,csFqdn.brand_match,csFqdn.keyword_match))
          
                if (csFqdn.score > 0.45 and csFqdn.score < 0.70 ):
                    csFqdn.fqdn_type = 'Likely Malicious'
                elif (csFqdn.score > 0.70):
                    csFqdn.fqdn_type = 'Malicious'
                elif (csFqdn.score < 0.45 and csFqdn.score > 0.25):
                    csFqdn.fqdn_type = 'Likely Benign'
                else:
                    csFqdn.fqdn_type = 'Benign'

               

             
       
                kw_list = list(csFqdn.keyword_match.values())

                #Get Brand Match

                
                #Get Keyword Match


                fi = FQDNInstance(fqdn_full=csFqdn.fqdn_full,fqdn_tested=csFqdn.fqdn,score=csFqdn.score,entropy=csFqdn.entropy,model_match='linearRegression',fqdn_subdomain=csFqdn.subdomain,fqdn_domain=csFqdn.domain,fqdn_type=csFqdn.fqdn_type)
                fi.save()
             
                for kw in kw_list:
                   
                    k = KeyWord.objects.get(pk=kw)
                   
                    fi.matched_keywords.add(k)
               
                
               
                #fi = FQDNInstance(csFqdn.fqdn_full,csFqdn.fqdn,csFqdn.fqdn_type,csFqdn.score, csFqdn.entropy,'linearRegression')
                #self.dbCursor.execute(insert_string,  (csFqdn.fqdn_full,csFqdn.fqdn,csFqdn.fqdn_type,csFqdn.score, csFqdn.entropy,'linearRegression'))
               
                #self.dbConnection.commit()
                return

            
    def execute_model (self,fqdns):
        """
        Takes a list of Fqdn instances, computes features, transforms to feature vector from training,
        and predicts them as phishing or not phishing (< or > 0.5).

        Args:
            fqdns (list): list of Fqdn objects to evaluate for phishing potential. 

        Return:
            result (list): Results from the evaluation from the trainer ex. [1.000, 0.981, 0.001].
        """
        
    
        features = self.attributes.compute_attributes(fqdns,speed=True)

        #function of algo
        scores = self.model.predict_proba(features['values'])[:,1]
       
        result = []
        for score in scores:
            if score > 0.15:
                result.append(score)


        return result

