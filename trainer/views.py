from django.shortcuts import render, HttpResponse, get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView,DetailView
from trainer.forms import ModelForm, FQDNInstanceForm
from trainer.models import Model, FQDNInstance
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
        model = form.save(commit=False)
        model.save()

        # Need to develop a thing that if the model fails to be created it removes the entry
        tasks.train_model.delay(model_name=model_name,model_id=model_id,model_description=model_description)
        return HttpResponseRedirect(self.get_success_url())
     
    def get_success_url(self):
        return reverse_lazy('models')  

class FQDNInstanceListView(ListView):
    model = FQDNInstance
    paginate_by = 20        
    context_object_name = 'fqdn_list'
    
    def get_context_data (self,**kwargs):
        
        context = super(FQDNInstanceListView,self).get_context_data(**kwargs)
       
        
        paginator = context['paginator']
        

        page_numbers_range = 10  
        start_idx = len(paginator.page_range)
        page = self.request.GET.get('page')
        current_page = int(page) if page else 1
        start_index = int((current_page - 1) / page_numbers_range) * page_numbers_range
        stop_idx = start_index + page_numbers_range
        if stop_idx >= start_idx:
            stop_idx = start_idx

        page_range = paginator.page_range[start_index:stop_idx]
        context['page_range'] = page_range
        return context

    def  get_queryset(self):
        return FQDNInstance.objects.all().filter(score__gte=0.75)

class FQDNInstanceDetails (UpdateView):
    model =  FQDNInstance
    form_class = FQDNInstanceForm
    context_object_name = 'fqdn'
    template_name = 'trainer/fqdninstance_detail.html'
    
   # form_class  = FQDNInstanceForm
    def get_context_data (self,**kwargs):
        
        context = super(FQDNInstanceDetails,self).get_context_data(**kwargs)
        context['keywords'] = ["Keyword 1","Keyword 2","Keyword 3"]#[kw.keyword for kw in context['fqdn'].matched_keywords.all()]
        context['brands'] =  [br.brand_name for br in context['fqdn'].matched_brands.all()]

        return context

    def form_valid(self, form):
        model = form.save(commit=True)
        model.save()

        # Need to develop a thing that if the model fails to be created it removes the entry
        
        return  HttpResponseRedirect(self.get_success_url())
   
    def get_success_url(self):
        return reverse_lazy('home')  

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

