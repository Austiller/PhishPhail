from django.shortcuts import render, HttpResponse, get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView,DetailView
from trainer.forms import ModelForm
from trainer.models import Model
import trainer.tasks as tasks

from django.template.defaultfilters import slugify



def updateTrainingData(request):
    context = {}
    return render(request,'trainer/trainer_upload.html',context)



# Model Form create 
class ModelCreateView (CreateView):
    """
        Class handles creating a new model for training. 

        -- Need to add field to form allowing user to drop down what training set they wish to use. 

    
    """

    model = Model
    form_class = ModelForm
    template_name = 'trainer/model_form.html'
        
    def form_valid(self, form):
        model = form.save(commit=True)
        

        # Need to develop a thing that if the model fails to be created it removes the entry
        tasks.train_model.delay(model_id=model.id)
      
        return HttpResponseRedirect(self.get_success_url())
     
    def get_success_url(self):
        return reverse_lazy('models')  


def homeView(request):
    context = {}
    return render(request, 'home.html')


def trainerSettings(request):
    context = {}
    return render(request,'trainer_settings.html',context=context)

class ModelListView (ListView):
    model = Model
    context_object_name = 'model_list'

    def get_context_data (self,**kwargs):
        context  = {}
        context['model_list'] = Model.objects.all()
        return context

