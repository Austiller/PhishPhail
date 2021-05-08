
from celery import shared_task
from trainer.models import Model as SavedModel
from modeler.model import Modeler
import threading 
import certstream
import pickle 

# The @shared_task decorator lets you create tasks without having any concrete app instance:
@shared_task
def start_model(model_id):
    modelToRun = SavedModel.objects.get(pk=model_id)
    all_processes = []
    att = pickle.loads(data=modelToRun.model_attributes, encoding='bytes')
    mod = pickle.loads(data=modelToRun.model_binary, encoding='bytes')
    m = Modeler(att,mod)

    t = threading.Thread(target=m.__call__ ,name=str(model_id),daemon=True)

    t.start()
    
    return