import  re,tldextract,logging
#from stringdist import levenshtein
#from Levenshtein import distance
from collections import OrderedDict
from datetime import time
from fqdn.models import FQDN
from phishFail.settings import FQDN_THRESHOLD

class Fqdn:
    """
    Represents an FQDN seen by the cert stream


    args:
        fqdn (str)
    
    """

    def __init__(self,fqdn,clean_fqdn:str=None,fqdn_type='Unknown',issuing_ca=None,root_ca=None,cert_seen=None,subdomain=None,domain=None,tld=None,score=None):
        self.fqdn_full = fqdn
        self.fqdn = clean_fqdn
        self.fqdn_type = fqdn_type
        self.keyword_match = {}
        self.brand_match = {}
        self.squatedWords = {}
        self.issuingCA = None
        self.rootCA= root_ca
        self.dateSeen = None
        self.fqdnParts =  tldextract.extract(fqdn)
        self.words =  re.split('\W+', fqdn)
        self.subdomain =  self.fqdnParts.subdomain
        self.domain = self.fqdnParts.domain
        self.tld = self.fqdnParts.suffix
        self.score = score
        self.entropy = None

    @classmethod
    def from_training_set (cls,fqdn_full:str,fqdn_type:str="Unknown"):
        return Fqdn(fqdn=fqdn_full,clean_fqdn=Fqdn.clean_fqdn(fqdn_full),fqdn_type=fqdn_type)

    @classmethod
    def from_certstream (cls,fqdn_full:str,fqdn_type:str='Unknown',issue_ca:str=None,root_ca:str=None):
        """ 
            Instantiate an FQDN from a certstream

            args:
                fqdn_full (str): The fqdn found in the stream
                fqdn_type (str), default 'Unknown': The type of FQDN
                issue_ca (str): The issuer of the CA
                root_ca (str): The root CA issuer
            
            returns:
                Fqdn 
            
        """
        fqdn  = cls(fqdn=fqdn_full,clean_fqdn=Fqdn.clean_fqdn(fqdn_full),fqdn_type=fqdn_type,issuing_ca=issue_ca,root_ca=root_ca)
        return fqdn

    @property
    def for_dabase (self):
        #fqdn_full=csFqdn.fqdn,fqdn,score=csFqdn.score,entropy=csFqdn.entropy,model_match='linearRegression',fqdn_subdomain=csFqdn.subdomain,fqdn_domain=csFqdn.domain,fqdn_type=csFqdn.fqdn_type

        #score=csFqdn.score,entropy=csFqdn.entropy,fqdn_subdomain=csFqdn.subdomain,fqdn_domain=csFqdn.domain,fqdn_type=csFqdn.fqdn_type
        return {"score":self.score,"fqdn_type":self.fqdn_type,"entropy":self.entropy,"fqdn_domain":self.domain,"fqdn_subdomain":self.subdomain}
        
    def get_type_as_int (self)-> int: 
        if(self.fqdn_type.startswith('m')):
            return 1
        else:
            return 0
    
    @staticmethod
    def clean_fqdn (fqdn)-> str: 
        """ 
        Takes the provided FQDN and removes common subdomains.

        args:
            self
        
        returns:
            None
        
        """
    
        common_prefixes = ["*", "www", 'www1','www2',"mail", "cpanel", "webmail",
                        "webdisk", "autodiscover","uat"]
        
        split_fqdn = fqdn.split(".")

        if len(split_fqdn) > 1:
            fqdn  = ".".join([sf for sf in split_fqdn if sf not in common_prefixes])
            return fqdn


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


    def certstream_handler (self,message, context) -> None:
        # May remove, set cerstream flag instead to ignore heartbeats
        
        if message['message_type'] == "heartbeat":
            return
        
        #Removes wildcard certs and www.* certs
        if message['message_type'] == "certificate_update":

            csFqdnList = message['data']['leaf_cert']['all_domains']
           
            ca_info = message['data']['leaf_cert']['issuer'].get('O','N/A')

            for csFqdn in csFqdnList:
                if csFqdn[:2]== '*.' and (csFqdn[2:] in csFqdnList):
                    csFqdnList.remove(csFqdn)

                elif csFqdn[4:] == "www." and (csFqdn[4:] in csFqdnList):
                    csFqdnList.remove(csFqdn)


               
            # 'Convert' found domains to a list Fqdn class. This will make updating the FQDNInstance table easier with the FQDN properties. 
            csFqdnList = [Fqdn.from_certstream(fqdn_full=csFqdn,fqdn_type='unknown') for csFqdn in csFqdnList]

  
            try:

                scores = self.execute_model(csFqdnList)
                
            except Exception as error:
                
                # Write to system.log, assign prediction score of 0, continue.
                logging.error("{}: {}".format(error, message))
                scores = ([0] * len(csFqdnList))
               
            for csFqdn,score in zip(csFqdnList,scores):
                #update database. 

                csFqdn.score = score


                if (csFqdn.score > 0.45 and csFqdn.score <= 0.70 ):
                    csFqdn.fqdn_type = 'Likely Malicious'
                elif (csFqdn.score > 0.70):
                    csFqdn.fqdn_type = 'Malicious'
                elif (csFqdn.score <= 0.45 and csFqdn.score >= 0.25):
                    csFqdn.fqdn_type = 'Likely Benign'
                else:
                    csFqdn.fqdn_type = 'Benign'



                new_fqdn,created = FQDN.objects.get_or_create(fqdn_full=csFqdn.fqdn)
                
                if created:
                    return new_fqdn
                else:
                    if csFqdn.score >= FQDN_THRESHOLD:
                        
                        for k,v in csFqdn.for_dabase.items():
                            setattr(new_fqdn,k,v)

                        
                        # Match on brands
                        new_fqdn.save()
             


                    return new_fqdn

            
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

