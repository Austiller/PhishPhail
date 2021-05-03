from django.shortcuts import render, HttpResponse, get_object_or_404,reverse,HttpResponseRedirect
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView,DeleteView
# Create your views here.
from background_task import background
from modeler.forms import  ExecuteModel
from trainer.models import Model
import trainer.views as tViews
from modeler.model import Modeler
import certstream
import pickle 
from modeler.forms import ModelEdit
from modeler.models import FoundFQDN
from background_task.models import CompletedTask
from os import system
from .models import *
import threading 
from trainer.models import FQDNInstance
import csv

@background
def runModel (request, pk):
    return render()

def csvAll (request):

    

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fqdnreport.csv"'
    writer = csv.writer(response)


   
    data = FQDNInstance.objects.all()
    
    cols = [f.name for f in FQDNInstance._meta.fields]
    writer.writerow(cols)    
    for row in data:
        rowobj = []
        for c in cols:
            rowobj.append(getattr(row,c))

        writer.writerow(rowobj)

    return response


def csvMalicious (request):

    

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fqdnreport.csv"'
    writer = csv.writer(response)
   
    data = FQDNInstance.objects.filter(score__gte=0.75)
    
    cols = [f.name for f in FQDNInstance._meta.fields]
    writer.writerow(cols)    
    for row in data:
        rowobj = []
        for c in cols:
            rowobj.append(getattr(row,c))

        writer.writerow(rowobj)

    return response


class ModelDeleteView  (DeleteView):
    model = Model
    template_name =  'models/model_confirm_delete.html'
    success_url = reverse_lazy('models')


class ModelEdit (UpdateView):
    """

        This function checks to see if the model can be run. If not it returns a message stating as such and steps the user can take. 


    """

    model = Model
    form_class = ModelEdit
    template_name =  'models/model_details.html'

    #If the form is valid, pass the primary key referencing the model to be executed.    
    def form_valid(self, form):
        model = form.save(commit=True)
        request = self.request

        return HttpResponseRedirect(reverse('models'))


    def get_success_url(self):
        return reverse_lazy('models')

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
    return# JsonResponse({'id':process.name})



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
    
    model.model_running = True
    model.save()
    mpk = model.pk
    
    # run one model at a time, stop all other models
    for m in Model.objects.exclude(id=mpk):
        m.model_running = False
        m.save()
        

    start_certstream_task(model.id)
    

    #Check if Model is already running
    #currentTask = CertStreamTask.objects.get(model_id=pk,is_running=True)

        
    #ml = ModelListView()
    
    
    return HttpResponseRedirect(reverse('models'))

 
def stopModel (request, pk):
    context = {}
    model = Model.objects.get(pk=pk)

    model.model_running = False
    model.save()

    

    return HttpResponseRedirect(reverse('models'))