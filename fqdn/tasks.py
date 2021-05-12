from celery import Celery
from celery import schedules
from celery.schedules import crontab
from phishFail.celery import app
from trainer.models import FQDNInstance as TfqdnInstance
from threading import Thread
from fqdn.models import FQDNInstance,KeyWord,Brand
from concurrent.futures import ThreadPoolExecutor,as_completed
from django.db.utils import IntegrityError

def check_for_matches (fqdn,keywords,brands):
    
    
    f_fqdn = FQDNInstance(fqdn_full=fqdn.fqdn_full,fqdn_tested=fqdn.fqdn_tested,score=fqdn.score,fqdn_type=fqdn.fqdn_type,
                            model_match=fqdn.model_match,fqdn_subdomain=fqdn.fqdn_subdomain,fqdn_domain=fqdn.fqdn_domain)
            
    try:
        f_fqdn.save()
        fqdn.delete()
    except IntegrityError:
        fqdn.delete()
        return 1
    matched_brands = [b for b in f_fqdn.check_brand(brands)]
    matched_keywords = [b for b in f_fqdn.check_keyword(keywords)] 
    if len(matched_keywords) > 1:
        f_fqdn.matched_keywords.add(*matched_keywords)

    if len(matched_brands) > 1:
        f_fqdn.matched_brands.add(*matched_brands)

    f_fqdn.save()
    fqdn.delete()

    return 1
    
@app.task(name="fetch_found_fqdn")
def fetch_found_fqdn (*args):
    """
    
    """
    fls = 10
    
    fqdn_list = TfqdnInstance.objects.all()
    if len(fqdn_list) < 1:
        return 1
    keywords = KeyWord.objects.all()
    brands = Brand.objects.all()
    

    fqdn_list = [check_for_matches(fqdn,keywords,brands) for fqdn in fqdn_list] 



    return 1


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    
    sender.add_periodic_task(60.0, fetch_found_fqdn.s(), name='match_fqdn_every_30')

  