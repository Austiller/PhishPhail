from django.db import models
from trainer.models import Model
# Create your models here.






class ModelerTask(models.Model):
    task_name = models.CharField(max_length=30, blank=True, null=True)
    task = models.BinaryField(null=True)
    status = models.CharField(max_length=30,blank=True,null=True)
    model_id = models.IntegerField(null=True)


