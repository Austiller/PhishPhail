from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
# Create your views here.
from background_task import background
from modeler.forms import  ExecuteModel
from trainer.models import Model
from modeler.model import Modeler
import certstream
import pickle 
from modeler.models import FoundFQDN
from background_task.models import CompletedTask
from os import system
from .models import *
import threading 



@background
def runModel (request, pk):
    return render()

    
def viewModel (request, pk):
    return render()

@background(name="certstream")
def start_certstream_task(model_id):
    modelToRun = Model.objects.get(pk=model_id)
    all_processes = []
    att = pickle.loads(data=modelToRun.model_attributes, encoding='bytes')
    mod = pickle.loads(data=modelToRun.model_binary, encoding='bytes')
    m = Modeler(att,mod)

    t = threading.Thread(target=m.__call__ ,name=str(model_id),daemon=True)

    t.start()
    return JsonResponse({'id':process.name})



@background
def clear_stuff():
    FoundFQDN.objects.all().delete()
    print("Deleted All FQDNs")
    CompletedTask.objects.all().delete()


def startModel (request, pk):
    context = {}
    #Trigger 

    #Trigger dialogue box to start the model?

    #Stop all other running models. Eventually set it so only urls above the threshold are the ones that are saved for all models running but the defualt. 
    # or have the models run against the database after populated by the default model. 

    model = Model.objects.get(pk=pk)
    start_certstream_task(model.id)


    #Check if Model is already running
  #  currentTask = CertStreamTask.objects.get(model_id=pk,is_running=True)




    #If not, Stop other models running, then start model


    #Else start model





   # run_model('1', repeat=10)
   # clear_stuff(repeat=30)
   


    return render(request,'trainer_settings.html',context=context)

 
def stopModel (request, pk):
    context = {}


    return render(request,'base.html',context=context)