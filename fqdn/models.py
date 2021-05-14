import fqdn
from django.db import models
# Create your models here.
from taggit.managers import TaggableManager

from django.db.models import  UniqueConstraint



class Brand(models.Model):
    """A Model used to define the brand names to be monitored for typo-squating"""
    brand_name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True,max_length=64,null=False)
    tags = TaggableManager()

    
    def __str__(self):
        return self.brand_name

    def __unicode__(self):
        return self.brand_name
    @property
    def get_slug_name(self):
        return self.brand_name
    @property
    def required_fields (self):
        return {"name":"brand_name","tags":"tags"}

class KeyWord(models.Model):
    keyword = models.CharField(max_length=200)
  
    slug = models.SlugField(unique=True,max_length=64,null=False)
    tags = TaggableManager(related_name="fqdn_kw_tags")

    def __str__(self):
        return self.keyword

    def __unicode__(self):
        return self.keyword

    @property
    def get_slug_name(self):
        return self.keyword

    @property
    def required_fields (self):
        return {"name":"keyword","tags":"tags"}

class TopLevelDomain(models.Model):
    tld = models.CharField(max_length=10)
    slug = models.SlugField(unique=True,max_length=64,null=True)
    tags = TaggableManager()
    

    def __str__(self):
        return self.tld

    def __unicode__(self):
        return self.tld
    
    @property
    def get_slug_name(self):
        return self.tld

    @property
    def required_fields (self):
        return {"name":"tld","tags":"tags"}

class SquatedWord (models.Model):
    """Words that are likely to be typosquated."""
    squated_word = models.CharField(max_length=200)
    slug = models.SlugField(unique=True,max_length=64,null=True)
    tags = TaggableManager()


    def __str__(self):
        return self.squ

    def __unicode__(self):
        return self.squated_word
    @property
    def get_slug_name(self):
        return self.squated_word
    @property
    def required_fields (self):
        return {"name":"squated_word","tags":"tags"}
class DomainPrefix(models.Model):
    """List of common hosts used by trainer."""

    domain_prefix = models.CharField(max_length=50)
    slug = models.SlugField(unique=True,max_length=64,null=True)
    

    def get_prefixes(self):
        return self.domain_prefix

    def __str__(self):
        return self.domain_prefix

    def __unicode__(self):
        return self.domain_prefix



# Change name to FoundFQDN
class FQDNInstance(models.Model):

  
    fqdn_full = models.CharField(max_length=512,null=True)
    fqdn_tested =  models.CharField(max_length=512,null=True)
    fqdn_type = models.CharField(max_length=25,null=True)
    score = models.FloatField(null=True,default=0.0)

    model_match = models.CharField(max_length=128,null=True)
    fqdn_subdomain = models.CharField(null=True,max_length=200)
    fqdn_domain = models.CharField(null=True,max_length = 200)


    # The date which the FQDN was seen
    date_seen = models.DateTimeField(auto_now_add=True)
    
    # If the domain of the FQDN matches a tracked brand
    matched_brands = models.ManyToManyField(Brand)
    matched_keywords =  models.ManyToManyField(KeyWord)
    
    tags = TaggableManager()
    # The Calculated randomness of the FQDN
    entropy = models.FloatField(default=0.0,null=True)

    class Meta:
        constraints = [ UniqueConstraint(fields=['fqdn_full'], name='unique_found_fqdn')]

    
    def check_keyword(self,keywords):
        for obj in keywords:
            if obj.keyword.lower() in self.fqdn_subdomain.lower():
                yield obj
            elif obj.keyword.lower() in self.fqdn_domain.lower():
                yield obj
            else:
                continue
    
    def check_brand (self,brands):
        for obj in brands:
      
            if obj.brand_name.lower() == self.fqdn_subdomain.lower():
               
                yield obj
                
            elif obj.brand_name.lower() == self.fqdn_domain.lower():
               
                
                yield obj
            else:
              
                
                continue

    def for_training (self):

        as_dict = {"model": "trainer.fqdn", "pk": self.id,"fields":{"fqdn":self.fqdn_full,
            "fqdn_type":self.fqdn_type,
            "for_training":True,
            }
        }
        return as_dict

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

        return