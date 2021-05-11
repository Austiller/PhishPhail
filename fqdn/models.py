from django.db import models
# Create your models here.
from taggit.managers import TaggableManager






class Brand(models.Model):
    """A Model used to define the brand names to be monitored for typo-squating"""
    brand_name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True,max_length=64,null=False)
    tags = TaggableManager()

    
    def __str__(self):
        return self.brand_name

    def __unicode__(self):
        return self.brand_name

class KeyWord(models.Model):
    keyword = models.CharField(max_length=200)
  
    slug = models.SlugField(unique=True,max_length=64,null=False)
    tags = TaggableManager(related_name="fqdn_kw_tags")

    def __str__(self):
        return self.keyword

    def __unicode__(self):
        return self.keyword

class TopLevelDomain(models.Model):
    tld = models.CharField(max_length=10)
    slug = models.SlugField(unique=True,max_length=64,null=True)
    tags = TaggableManager()
    

    def __str__(self):
        return self.tld

    def __unicode__(self):
        return self.tld



class SquatedWord (models.Model):
    """Words that are likely to be typosquated."""
    squated_word = models.CharField(max_length=200)
    slug = models.SlugField(unique=True,max_length=64,null=True)
    tags = TaggableManager()


    def __str__(self):
        return self.squ

    def __unicode__(self):
        return self.squated_word

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




class FQDNInstance(models.Model):

  
    fqdn_full = models.CharField(max_length=512,null=True)
    fqdn_tested =  models.CharField(max_length=512,null=True)
    fqdn_type = models.CharField(max_length=25,null=True)
    score = models.FloatField(null=True,default=0.0)
    tags = TaggableManager()
    model_match = models.CharField(max_length=128,null=True)
    fqdn_subdomain = models.CharField(null=True,max_length=200)
    fqdn_domain = models.CharField(null=True,max_length = 200)


    # The date which the FQDN was seen
    date_seen = models.DateTimeField(auto_now_add=True)
    
    # If the domain of the FQDN matches a tracked brand
    matched_brands = models.ManyToManyField(Brand)
    
    matched_keywords =  models.ManyToManyField(KeyWord)
    # The Calculated randomness of the FQDN
    entropy = models.FloatField(default=0.0,null=True)