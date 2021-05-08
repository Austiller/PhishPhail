from phishFail.celery import app
from trainer.trainer import AttributeManager,Trainer

from celery import shared_task

#@app.task
@shared_task
def train_model(model_name,model_id):
    # Get all FQDNs for training
  
    t = Trainer(name=model_name,model_id=model_id)
    
    t.train_model()

    return 1