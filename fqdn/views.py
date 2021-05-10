from django.shortcuts import render
from .models import KeyWord,Brand,FQDNInstance
from django.shortcuts import render, HttpResponse, get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView,DetailView
from .forms import KeyWordForm
from .models import FQDNInstance,KeyWord,Brand,SquatedWord
# Create your views here.
from django.template.defaultfilters import slugify


def tagged(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    # Filter posts by tag name  
    keywords = KeyWord.objects.filter(tags=tag)
    context = {
        'tag':tag,
        'posts':keywords,
    }
    return render(request, 'home.html', context)

def keyword_details (request):
    keywords = KeyWord.objects.order_by('keyword')

    common_categories = KeyWord.keyword_tags.most_common()[:3]
    form = KeyWordForm

    if form.is_valid():
        new_keyword = form.save(commit=False)
        new_keyword.slug = slugify(new_keyword.keyword)
        form.save()
        form.save_m2m()
    context = {
        'keywords':keywords,
        'common_categories':common_categories,
        'form':form
    }
    return render(request,'fqdn/keyword_form.html')

class KeyWordCreateView (CreateView):
    model = KeyWord
    form_class = KeyWordForm
    template_name = 'trainer/keyword_form.html'
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