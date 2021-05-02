from django.db import models
from trainer.models import Model
# Create your models here.


class FoundFQDN (models.Model):

    fqdn = models.CharField(max_length=512,null=True)


    def __str__ (self):
        return self.fqdn



class CertStreamTask(models.Model):
    task = models.CharField(max_length=30, blank=True, null=True)
    is_running =  models.BooleanField(blank=False,default=False )
   # model_id = models.ForeignKey(Model,default=0,)