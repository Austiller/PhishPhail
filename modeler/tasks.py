
from celery import shared_task
from trainer.models import Model as SavedModel
from modeler.model import Modeler
import pickle 
from certstream.core import CertStreamClient
# The @shared_task decorator lets you create tasks without having any concrete app instance:
from time import sleep
from threading import Thread
from phishFail.celery import app
    

@app.task(name="certstream")
def start_model(model_id)->int:
    """Creates a task to start the certstream model, continues to check if model should be run. If model_running is set to false will stop the stream and worker.

        args:
            model_id (int): The model_id of the model to run on the certstream
        returns
            model_id (int): The model_id of the model running on the certstream
    
    """
    run = True
    modelToRun = SavedModel.objects.get(pk=model_id)
    m = Modeler(attributes=pickle.loads(data=modelToRun.model_attributes, encoding='bytes'),
        model=pickle.loads(data=modelToRun.model_binary, encoding='bytes'))
    
    while run:
        c = CertStreamClient(message_callback=m.certstream_handler, url='wss://certstream.calidog.io/', skip_heartbeats=True, on_open=None, on_error=None,)
        c.keep_running = run
        c.run_forever(ping_interval=15)
        #cert_thread = Thread(target=c.run_forever,kwargs={"ping_interval":15})
        #cert_thread.start()
        sleep(5)
        run =  SavedModel.objects.get(pk=model_id).model_running
        c.keep_running = run
    
    
    return model_id