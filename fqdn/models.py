import fqdn, tldextract,re
from django.db import models
# Create your models here.
from taggit.managers import TaggableManager
from Levenshtein import distance
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

class CloudPlatform (models.Model):
    """Words that are likely to be typosquated."""
    platform = models.CharField(max_length=200)
    slug = models.SlugField(unique=True,max_length=64,null=True)
    tags = TaggableManager()


    def __str__(self):
        return self.squ

    def __unicode__(self):
        return self.platform
    @property
    def get_slug_name(self):
        return self.platform
    @property
    def required_fields (self):
        return {"name":"platform","tags":"tags"}


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
class FQDN(models.Model):

  
    fqdn_full = models.CharField(max_length=512,null=True)
    
    fqdn_type = models.CharField(max_length=25,null=True)
    score = models.FloatField(null=True,default=0.0)

    
    fqdn_subdomain = models.CharField(null=True,max_length=200)
    fqdn_domain = models.CharField(null=True,max_length = 200)
    fqdn_tld = models.CharField(null=True,max_length=6)
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
            try:
                if obj.slug in self.fqdn_subdomain.lower():
                    yield obj
                elif obj.slug in self.fqdn_domain.lower():
                    yield obj
                else:
                    continue
            except Exception:
                continue
            
    def check_brand (self,brands):
        for obj in brands:
            for word in self.fqdn_words:
                dist = 0 if len(obj.slug) < 5 else distance(word,obj.slug)
                if obj.slug == word:
                    yield obj
                elif dist == 1:
                    yield obj

            #if obj.slug == self.fqdn_subdomain.lower():
               
             #   yield obj
                
            #elif obj.slug == self.fqdn_domain.lower():
               
             #   yield obj

            #else:
                
                
             #   continue
        

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
    
    @property
    def fqdn_words(self):
        """ #Split the domain by non-alphanumeric characters."""
        return re.split("\W+", self.fqdn_full)
    
    def __unicode__(self):
        return self.fqdn_full

    def __str__(self):
        return self.fqdn_full
