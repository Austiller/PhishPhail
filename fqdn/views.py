from typing import List
from django.forms.widgets import MultipleHiddenInput
from django.shortcuts import render
from .models import KeyWord,Brand,FQDNInstance
from django.shortcuts import render, HttpResponse, get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView,DetailView
from fqdn.forms import BrandForm, KeyWordForm, KeywordUpdate
from fqdn.models import FQDNInstance,KeyWord,Brand,SquatedWord
# Create your views here.
from django.template.defaultfilters import slugify
from taggit.models import Tag
from fqdn import models


def tagged_kw(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    common_tags = KeyWord.tags.most_common()[:4]
    keywords = KeyWord.objects.filter(tags=tag)
    context = {
        'tag':tag,
        'common_tags':common_tags,
        'keywords':keywords,
    }
    return render(request, 'fqdn/keyword_list.html', context)

def tagged_brands(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    common_tags = Brand.tags.most_common()[:4]
    brands = Brand.objects.filter(tags=tag)
    context = {
        'tag':tag,
        'common_tags':common_tags,
        'brands':brands,
    }
    return render(request, 'fqdn/brand_list.html', context)

def brand_update (request,slug):
    return


 


def brand_detail(request, slug):
    brand = get_object_or_404(Brand, slug=slug)
    common_tags = brand.tags.most_common()[:4]
    
    form = KeywordUpdate(request.POST)

    if request.method == "POST":
        
        if form.is_valid():
            brand.brand_name = brand.brand_name
            brand.tags.add(*form.cleaned_data['tags'])
            brand.save()
    context = {
        'brand':brand,
        'common_tags':common_tags,
        'form':form,

    }
        
        
    return render(request, 'fqdn/brand_detail.html', context)
   


def brand_list(request):
    brands = Brand.objects.all()
    common_tags = Brand.tags.most_common()[:4]
  
    form = BrandForm(request.POST)
    context = {
        'brands':brands,
        'common_tags':common_tags,
        'form':form,
    }
    
    if request.method == "POST":
        if form.is_valid():   
            new_brand = form.save(commit=False)
            new_brand.slug = slugify(new_brand.brand_name)
            new_brand.save()
            
            form.save_m2m()
        else:
            return HttpResponse(form.errors)
  
    return render(request, 'fqdn/brand_list.html', context)



def keyword_list(request):
    keywords = KeyWord.objects.all()
    common_tags = KeyWord.tags.most_common()[:4]
    form = KeyWordForm(request.POST)
    if form.is_valid():
        new_kw = form.save(commit=False)
        new_kw.slug = slugify(new_kw.keyword)
        new_kw.save()
        form.save_m2m()
    context = {
        'keywords':keywords,
        'common_tags':common_tags,
        'form':form,
    }
    return render(request, 'fqdn/keyword_list.html', context)


def kw_detail_view(request, slug):
    kw = get_object_or_404(KeyWord, slug=slug)
    common_tags = kw.tags.most_common()[:4]
    
    form = KeywordUpdate(request.POST)

    if request.method == "POST":
        
        if form.is_valid():
            kw.keyword = kw.keyword
            kw.tags.add(*form.cleaned_data['tags'])
            kw.save()
    context = {
        'keyword':kw,
        'common_tags':common_tags,
        'form':form,

    }
        
        
    return render(request, 'fqdn/keyword_detail.html', context)
   



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