from phishFail.celery import app
from trainer.trainer import AttributeManager,Trainer

@app.task
def train_model(model_name,model_id):
    # Get all FQDNs for training
  
    t = Trainer(name=model_name,model_id=model_id)
    
    t.train_model()

    return 1