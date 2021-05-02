from django.shortcuts import render, HttpResponse, get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView,DetailView
from background_task import background
from .models import FQDN,Model
from trainer.trainer import AttributeManager,Trainer
from trainer.forms import ModelForm,  ModelDetails, ModelEdit
from trainer.models import Model, FQDNInstance, KeyWord 
from .forms import ModelForm


@background(name="Train_Model")
def train_model(modelName,model_id):
    # Get all FQDNs for training
  
    t = Trainer(name=modelName,model_id=model_id)
    
    return 1



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
        model = form.save(commit=False)
        model.save()

        # Need to develop a thing that if the model fails to be created it removes the entry
        train_model(model.model_name,model.id)
        return HttpResponseRedirect(self.get_success_url())
     
    def get_success_url(self):
        return reverse_lazy('models')  

class FQDNInstanceListView(ListView):
    model = FQDNInstance
    paginate_by = 100
   # context_object_name = 'fqdn_list'
    def get_context_data (self,**kwargs):
        context  = {}
        context['fqdn_list'] = FQDNInstance.objects.all().filter(score__gte=0.5)
        return context

def fqdninstance_details (request,pk):
    context = {}
    context['fqdn'] = FQDNInstance.objects.get(pk=pk)
    context['keywords'] = []
    for kw in context['fqdn'].matched_keywords.all():
        context['keywords'].append(kw.keyword)
        print(context)
    return render(request,'trainer/fqdninstance_detail.html',context)




class ModelUpdateView(UpdateView):
    model = Model
    form_class = ModelForm
    template_name = 'trainer/model_form.html'
    success_url = reverse_lazy('models')
    

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



class ModelEdit (UpdateView):
    """

        This function checks to see if the model can be run. If not it returns a message stating as such and steps the user can take. 


    """

    model = Model
    form_class = ModelEdit
    template_name = 'trainer/model_details.html'

    #If the form is valid, pass the primary key referencing the model to be executed. 
    def form_valid(self, form):
        model = form.save(commit=True)
        request = self.request

        return HttpResponseRedirect(reverse('models'))


    def get_success_url(self):
        return reverse_lazy('models')


