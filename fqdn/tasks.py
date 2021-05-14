from celery import Celery
from celery import schedules
from celery.schedules import crontab
from phishFail.celery import app
from trainer.models import FQDNInstance as TfqdnInstance
from threading import Thread
from fqdn.models import FQDNInstance,KeyWord,Brand
from concurrent.futures import ThreadPoolExecutor,as_completed
from django.db.utils import IntegrityError
from django.db.models import prefetch_related_objects

def update_tags (fqdn,matched_keywords=None,matched_brands=None):

  
    # rewrite this to better use the queryset api
    if matched_keywords != None:
        tags = []
        for keyword in matched_keywords:
            kw_tags = keyword.tags.all()
            tags.extend([kt.name for kt in kw_tags])

        fqdn.tags.add(*tags)
        
    if matched_brands != None:
        tags = []
        for brand in matched_brands:
            brand_tags = brand.tags.all()
            tags.extend([bt.name for bt in brand_tags])

        fqdn.tags.add(*tags)
   
    fqdn.save()
    return fqdn

def check_for_matches (fqdn,keywords,brands):
    
    matched_brands = []
    matched_keywords = []
    
    f_fqdn, created = FQDNInstance.objects.get_or_create(fqdn_full=fqdn.fqdn_full,fqdn_tested=fqdn.fqdn_tested,score=fqdn.score,fqdn_type=fqdn.fqdn_type,
                            model_match=fqdn.model_match,fqdn_subdomain=fqdn.fqdn_subdomain,fqdn_domain=fqdn.fqdn_domain)
            
    
    if keywords != None:
        matched_keywords = [kw for kw in f_fqdn.check_keyword(keywords)] 
        if len(matched_keywords) > 0:
            f_fqdn.matched_keywords.add(*[kw.id for kw in matched_keywords])

    if brands != None:
        
        matched_brands = [b for b in f_fqdn.check_brand(brands)]
        if len(matched_brands) > 0:
            f_fqdn.matched_brands.add(*[br.id for br in matched_brands])
    
    if len(matched_brands) > 0 or len(matched_keywords) > 0:
        f_fqdn.save()
        update_tags(f_fqdn,matched_keywords,matched_brands)
        
    if created:
        fqdn.delete()

    return 1

@app.task(name="rematch_brands")
def rematch_brands (*args):
    brands = Brand.objects.all()
    fqdn_list = FQDNInstance.objects.all()
    
    fqdn_list = [check_for_matches(fqdn=fqdn,keywords=None,brands=brands) for fqdn in fqdn_list] 

@app.task(name="rematch_keywords")
def rematch_keywords (*args):
    keywords = KeyWord.objects.all()
    fqdn_list = FQDNInstance.objects.all()
    
    fqdn_list = [check_for_matches(fqdn=fqdn,keywords=keywords,brands=None) for fqdn in fqdn_list] 


@app.task(name="fetch_found_fqdn")
def fetch_found_fqdn (*args):
    """
    
    """
    
    
    fqdn_list = TfqdnInstance.objects.all()
    if len(fqdn_list) < 1:
        return 1
    keywords = KeyWord.objects.all()#.prefetch_related("tags")
    brands = Brand.objects.all()
    

    fqdn_list = [check_for_matches(fqdn,keywords,brands) for fqdn in fqdn_list] 



    return 1


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    
    sender.add_periodic_task(60.0, fetch_found_fqdn.s(), name='match_fqdn_every_30')

  