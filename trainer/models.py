from django.db import models
import re
import tldextract
from collections import Counter

# Need to create view for training set 



class Tag (models.Model):

    tag_name = models.CharField(max_length=200)
 

    def __unicode__(self):
        return self.tag

    def __str__(self):
        return self.tag



class Brand(models.Model):
    """A Model used to define the brand names to be monitored for typo-squating"""
    brand_name = models.CharField(max_length=200)
    brand_category = models.ManyToManyField(Tag)

    
    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

class KeyWord(models.Model):
    keyword = models.CharField(max_length=200)
    keyword_tag = models.ManyToManyField(Tag)
  

    def __str__(self):
        return self.keyword

    def __unicode__(self):
        return self.keyword

class TopLevelDomain(models.Model):
    tld = models.CharField(max_length=10)
    tld_tags = models.ManyToManyField(Tag)
 

    def __str__(self):
        return self.tld

    def __unicode__(self):
        return self.tld



class SquatedWord (models.Model):
    """Words that are likely to be typosquated."""
    squated_word = models.CharField(max_length=200)
    squated_tag = models.ManyToManyField(Tag)


    def __str__(self):
        return self.squ

    def __unicode__(self):
        return self.squated_word

class DomainPrefix(models.Model):
    """List of common hosts used by trainer."""

    domain_prefix = models.CharField(max_length=50)
 

    def get_prefixes(self):
        return self.domain_prefix

    def __str__(self):
        return self.domain_prefix

    def __unicode__(self):
        return self.domain_prefix


class FQDN(models.Model):
    """Listing of FQDN found and categorized"""

    fqdnType_choices = (
        ('m','Malicious'),
        ('b', 'Benign'),
        ('u', 'Unknown')
    )


    fqdn = models.CharField(max_length=1000)
    
    fqdn_type = models.CharField(choices=fqdnType_choices,default='u',max_length=25)

    for_training = models.BooleanField("Use For Training",default=False)

    def number_dashes(self):
        return 0 if "xn--" in self.fqdn else self.count("-")

    def count_periods(self):
        return self.fqdn.count(".")

    def clean_fqdn(self,prefixes):
        """Split the FQDN up and removing common web-prefixes, ensures the FQDN used is the root-FQDN only."""

        split_fqdn = self.fqdn(".")

        if len(split_fqdn) > 1:
            if (split_fqdn[0] in prefixes):
                return split_fqdn[0]
            else:
                return self.fqdn

    def fqdn_parts(self):
        """Return a dictionary of the FQDN containing Subdomain, domain and TLD"""

        fqdn = tldextract.extract(self.fqdn)
        return {"domain":fqdn.domain,"subdomain":fqdn.subdomain,"suffix":fqdn.suffix}

    def fqdn_words(self):
        """ #Split the domain by non-alphanumeric characters."""
        return re.split("\W+", self.fqdn)
    
    def __unicode__(self):
        return self.fqdn

    def __str__(self):
        return self.fqdn

class FQDNInstance(models.Model):



    #The FQDN
   # fqdn_full = models.ForeignKey(FQDN, null=False, on_delete=models.CASCADE)


    fqdn_full = models.CharField(max_length=512,null=True)
    fqdn_tested =  models.CharField(max_length=512,null=True)

    fqdn_type = models.CharField(max_length=25,null=True)

    
    score = models.FloatField(null=True,default=0.0)

    # The name of the model used to match the FQDN
    model_match = models.CharField(max_length=128,null=True)

    fqdn_subdomain = models.CharField(null=True,max_length=200)

    fqdn_domain = models.CharField(null=True,max_length = 200)

    # If the domain of the FQDN matches a tracked brand
    matched_brands = models.ManyToManyField(Brand)
    
    matched_keywords =  models.ManyToManyField(KeyWord)

    # If the subdomain of the FQDN matches a tracked brand

    #brand_subdomain_match = models.ForeignKey(Brand)

    # The date which the FQDN was seen
    date_seen = models.DateTimeField(null=True)


    # The Calculated randomness of the FQDN
    entropy = models.FloatField(default=0.0,null=True)

class Model (models.Model):
    # Name of the Model
    model_name = models.CharField(default=False,max_length=128,null=False)
    model_description = models.CharField(default="",max_length=256,null=True)
    model_algorithm =  models.CharField(default=False,max_length=128,null=True)
    model_creation_date = models.DateTimeField(null=True,auto_now_add=True)
    
    # The number of malicious URLS used to train the model
    model_malicious_count = models.IntegerField(null=True,default=0)

    #The number of benign urls used to train the model
    model_benign_count = models.IntegerField(null=True,default=0)

    accuracy_precision = models.FloatField(null=True,default=0.0)

 
    # Accuracy of the model
    accuracy_training_set = models.FloatField(null=True,default=0.0)
    accuracy_test_set =  models.FloatField(null=True,default=0.0)

    accuracy_precision = models.FloatField(null=True,default=0.0)
    accuracy_recall = models.FloatField(null=True,default=0.0)

   
    model_running = models.BooleanField(default=False,null=True)

    #Model binary for replication later
    model_binary = models.BinaryField(null=True)
    model_attributes = models.BinaryField(null=True)
    
    #Is the model the current default
    set_as_default = models.BooleanField(default=False,null=True)

    def get_default_model(self):
        if(Model.set_as_default == True):
            return (Model.model_binary, Model.model_attributes)

    def clear_defaults(self):
        Model.set_as_default = False

    def __unicode__(self):
        return self.model_name

    def __str__(self):
        return self.model_name

