from sys import version
from phishFail.celery import app
from trainer.trainer import AttributeManager,Trainer

from celery import shared_task


@shared_task
def train_model(model_id:int):#model_name:str,model_id:int,model_description:str,model_version:float):
    # Get all FQDNs for training
  
    t = Trainer(model_id)
    

    return 1