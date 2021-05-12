from django.db import models

# Create your models here.






class ModelerTask(models.Model):
    task_name = models.CharField(max_length=30, blank=True, null=True)
    task = models.BinaryField(null=True)
    status = models.CharField(max_length=30,blank=True,null=True)
    model_id = models.IntegerField(null=True)


