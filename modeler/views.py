from sys import version
from django.shortcuts import render, HttpResponse, reverse,HttpResponseRedirect
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import   UpdateView, DeleteView
from trainer.models import Model
from modeler.forms import ModelEdit
from os import system
from modeler.models import * 
from trainer.models import FQDNInstance
import csv
from modeler.tasks import start_model
import pickle
from trainer.tasks import train_model
from trainer.models import Model as tModel

def csv_all (request):


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


def csv_malicious (request):

    

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
        new_version = form.cleaned_data['model_version']
        old_version = Model.objects.get(pk=self.object.id).model_version
       
        model = form.save(commit=False)
        
        if new_version != old_version:
            train_model.delay(model_id=model.id)
        
        model.save()

        return HttpResponseRedirect(reverse('models'))
        

    def get_success_url(self):
        return reverse_lazy('models')

def viewModel (request, pk):
    return render()





def start_certstream (request, pk):
    context = {}
    #Trigger 

    #Trigger dialogue box to start the model?

    #Stop all other running models. Eventually set it so only urls above the threshold are the ones that are saved for all models running but the defualt. 
    # or have the models run against the database after populated by the default model. 

  
    model = Model.objects.get(pk=pk)
    
    model.model_running = True
    model.save()
   
    
    # run one model at a time, stop all other models
    for m in Model.objects.exclude(id=model.pk):
        m.model_running = False
        m.save()


    task = start_model.delay(model_id=pk)
    modeler_task,created = ModelerTask.objects.get_or_create(model_id=pk)

    
    
    modeler_task.task_name = "CertStream"
    modeler_task.task=pickle.dumps(task)
    modeler_task.status="RUNNING"
    modeler_task.save()
    

    #Check if Model is already running
    #currentTask = CertStreamTask.objects.get(model_id=pk,is_running=True)

        
    #ml = ModelListView()
    
    
    return HttpResponseRedirect(reverse('models'))

 
def stop_certstream (request, pk):
    context = {}
    model = Model.objects.get(pk=pk)

    model.model_running = False
    model.save()

    model_task = ModelerTask.objects.get(model_id=pk)
    mt = pickle.loads(model_task.task)
    mt.revoke(terminate=True)
    model_task.task = b''
    model_task.status = "STOPPED"
    model_task.save()
    
    return HttpResponseRedirect(reverse('models'))