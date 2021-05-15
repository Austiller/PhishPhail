from typing import List
from django.forms.widgets import MultipleHiddenInput
from django.shortcuts import render
from django.shortcuts import render, HttpResponse, get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView,DetailView
from fqdn.forms import BrandForm, KeyWordForm, KeywordUpdate,SquatedWordForm
from fqdn.models import FQDN,KeyWord,Brand,SquatedWord
# Create your views here.
from django.template.defaultfilters import slugify
from taggit.models import Tag
from fqdn import models
from trainer.forms import FQDNInstanceForm
from fqdn.tasks import rematch_brands,rematch_keywords
import csv,json
from django.http import JsonResponse


def csv_all (request):


    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fqdnreport.csv"'
    writer = csv.writer(response)
   
    data = FQDN.objects.all()
    
    cols = [f.name for f in FQDN._meta.fields]
    writer.writerow(cols)    
    for row in data:
        rowobj = []
        for c in cols:
            rowobj.append(getattr(row,c))

        writer.writerow(rowobj)

    return response

def json_all (request):

    response = HttpResponse(content_type='text/json')
    response['Content-Disposition'] = 'attachment; filename="fqdnreport.json"'
    
   
    j_list = [] 
    
    for f in FQDN.objects.all():
       
        j_list.append(f.for_training())
     
    
    return JsonResponse(data=j_list,safe=False)

def csv_malicious (request):

    

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fqdnreport.csv"'
    writer = csv.writer(response)
   
    data = FQDN.objects.filter(score__gte=0.75)
    
    cols = [f.name for f in FQDN._meta.fields]
    writer.writerow(cols)    
    for row in data:
        rowobj = []
        for c in cols:
            rowobj.append(getattr(row,c))

        writer.writerow(rowobj)

    return response


def set_attribute_object(attribute_name):
    if attribute_name == "Brand":
        return Brand,BrandForm
    elif attribute_name == "SquatedWord":
        return SquatedWord, SquatedWordForm
    elif attribute_name == "KeyWord":
        return KeyWord, KeyWordForm



def attribute_tags(request,attribute_name, slug):
    tag = get_object_or_404(Tag, slug=slug)
    obj, form = set_attribute_object(attribute_name)
    common_tags = obj.tags.most_common()[:4]
    objs = obj.objects.filter(tags=tag)
    context = {
        'tag':tag,
        'common_tags':common_tags,
        'objects':objs,
        'object_name':attribute_name,
        'required_fields':objs[0].required_fields
    }
    return render(request, 'fqdn/attribute_tags.html', context)


def attribute_detail(request,attribute_name,slug):
    obj, form = set_attribute_object(attribute_name)
    objs = get_object_or_404(obj, slug=slug)
    
    common_tags = objs.tags.most_common()[:4]

    if request.method == "POST":
        form = form(request.POST)
        if form.is_valid():   
            new_obj = form.save(commit=False)
            new_obj.slug = slugify(new_obj.get_slug_name)
            new_obj.save()
            
            form.save_m2m()
           #

        else:
            input(form.errors)
            return HttpResponse(form.errors)
 

      
    context = {
        'object':objs,
        'common_tags':common_tags,
        'form':form,
        'object_name': attribute_name,
        'required_fields':objs.required_fields
    }
    
    
    return render(request, 'fqdn/attribute_details.html', context)
    
def attribute_list (request,attribute_name):
    print(attribute_name)
    obj, form = set_attribute_object(attribute_name)

    objs = obj.objects.all()
    # "{% url 'sw_tags' tag.slug %}"
    #"{% url 'view_kw_details' object.slug %}"
    common_tags = obj.tags.most_common()[:4]
    
    
   
    context = {
        'objects':objs,
        'common_tags':common_tags,
        'form':form,
        'object_name': attribute_name,
        'required_fields':objs[0].required_fields
    }
    
    if request.method == "POST":
        form = form(request.POST)
        if form.is_valid():   
            new_obj = form.save(commit=False)
            new_obj.slug = slugify(new_obj.get_slug_name)
            new_obj.save()
            
            form.save_m2m()
            if attribute_name == "Brand":
                rematch_brands.delay()
            elif attribute_name == "SquatedWord":
                rematch_keywords.delay()

        else:
            input(form.errors)
            return HttpResponse(form.errors)
 
    return render(request, 'fqdn/attribute_lists.html', context)


def refresh_brands (request):

    rematch_brands.delay()

    return HttpResponseRedirect(reverse_lazy('view_all_brands')  )

class FQDNInstanceListView(ListView):
    model = FQDN
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
        return FQDN.objects.all().filter(score__gte=0.75)


class FQDNInstanceDetails (UpdateView):
    model =  FQDN
    form_class = FQDNInstanceForm
    context_object_name = 'fqdn'
    template_name = 'fqdn/matched_fqdn_detail.html'
    
   # form_class  = FQDNInstanceForm
    def get_context_data (self,**kwargs):
        
        context = super(FQDNInstanceDetails,self).get_context_data(**kwargs)
        
        return context

    def form_valid(self, form):
        model = form.save(commit=True)
        model.save()

        # Need to develop a thing that if the model fails to be created it removes the entry
        
        return  HttpResponseRedirect(self.get_success_url())
   
    def get_success_url(self):
        return reverse_lazy('home')  