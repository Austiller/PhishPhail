from typing import List
from django.forms.widgets import MultipleHiddenInput
from django.shortcuts import render
from .models import KeyWord,Brand,FQDNInstance
from django.shortcuts import render, HttpResponse, get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView,DetailView
from fqdn.forms import BrandForm, KeyWordForm
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


class BrandDetailView (UpdateView):
    model =  Brand
    form_class = BrandForm
    context_object_name = 'brand'
    template_name = 'fqdn/brand_detail.html'
    
   # form_class  = FQDNInstanceForm
    def get_context_data (self,**kwargs):
        context = super(BrandDetailView,self).get_context_data(**kwargs)
        context['tags'] = context['brand'].tags.most_common()[:4]
        return context

    def form_valid(self, form):
       # curr_tags = self.object.tags.names()
        new_kw = form.save(commit=False)
        #input(new_kw.data.cleaned_data['tags'])
        new_kw.slug = slugify(new_kw.brand_name)
        new_kw.brand_name = new_kw.brand_name
        
        new_kw.save()
        form.save_m2m()
        

        # Need to develop a thing that if the model fails to be created it removes the entry
        
        return  HttpResponseRedirect(self.get_success_url())
   
    def get_success_url(self):
        return reverse_lazy('view_all_brands')  

class BrandCreateView (CreateView):
    model = Brand
    form_class = BrandForm
    template_name = 'fqdn/brand_form.html'
    def form_valid(self,form):

        model = form.save(commit=False)
        model.save()
        
        return HttpResponseRedirect(self.get_success_url())
          
    def get_success_url(self):
        return reverse_lazy('models')  


def brand_list(request):
    brands = Brand.objects.all()
    common_tags = Brand.tags.most_common()[:4]
    form = BrandForm(request.POST)
    if form.is_valid():
        new_brand = form.save(commit=False)
        new_brand.slug = slugify(new_brand.brand_name)
        new_brand.save()
        form.save_m2m()
    context = {
        'brands':brands,
        'common_tags':common_tags,
        'form':form,
    }
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

class KwDetailView (UpdateView):
    model =  KeyWord
    form_class = KeyWordForm
    context_object_name = 'keyword'
    template_name = 'fqdn/keyword_detail.html'
    
   # form_class  = FQDNInstanceForm
    def get_context_data (self,**kwargs):
        context = super(KwDetailView,self).get_context_data(**kwargs)
        context['tags'] = context['keyword'].tags.most_common()[:4]
        return context

    def form_valid(self, form):
       # curr_tags = self.object.tags.names()
        new_kw = form.save(commit=False)
        #input(new_kw.data.cleaned_data['tags'])
        new_kw.slug = slugify(new_kw.keyword)
        new_kw.keyword = new_kw.keyword
        
        new_kw.save()
        form.save_m2m()
        

        # Need to develop a thing that if the model fails to be created it removes the entry
        
        return  HttpResponseRedirect(self.get_success_url())
   
    def get_success_url(self):
        return reverse_lazy('view_all_keywords')  


def kw_detail_view(request, slug):
    kw = get_object_or_404(KeyWord, slug=slug)
    common_tags = kw.tags.most_common()[:4]
    
    form = KeyWordForm(request.POST)

    #if request.method == "POST":
    if form.is_valid():
        new_kw = form.save(commit=False)
        new_kw.slug = slugify(new_kw.keyword)
        new_kw.save()
        form.save_m2m()
    context = {
        'keyword':kw,
        'common_tags':common_tags,
        'form':form,

    }
        
        
    return render(request, 'fqdn/keyword_detail.html', context)
   


class KeyWordDetailView (UpdateView):
    model = KeyWord
    form_class = KeyWordForm
    template_name = 'fqdn/keyword.html'
    context_object_name = 'keyword'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        return context

class KeyWordCreateView (CreateView):
    model = KeyWord
    form_class = KeyWordForm
    template_name = 'fqdn/keyword_form.html'
    def form_valid(self,form):

        model = form.save(commit=False)
        model.save()
        
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