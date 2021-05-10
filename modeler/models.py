from django.db import models
from trainer.models import Model
# Create your models here.


class FoundFQDN (models.Model):

    fqdn = models.CharField(max_length=512,null=True)
    def __str__ (self):
        return self.fqdn



class ModelerTask(models.Model):
    task_name = models.CharField(max_length=30, blank=True, null=True)
    task = models.BinaryField(null=True)
    status = models.CharField(max_length=30,blank=True,null=True)
    model_id = models.IntegerField(null=True)


