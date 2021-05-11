from django.urls import path
from . import views
from django.urls import include
from trainer.views import FQDNInstanceDetails
from .views import FQDNInstanceListView, kw_detail_view 

urlpatterns = [
    path('',FQDNInstanceListView.as_view(),name='found_fqdn'),
    path('<int:pk>/details/', FQDNInstanceDetails.as_view(), name='view_fqdn_details'),
    path('keywords/',views.keyword_list,name="view_all_keywords"),
    path('keywords/add/', views.KeyWordCreateView.as_view(), name='create_kw'),
    path('keywords/<slug:slug>/details',views.KwDetailView.as_view(),name="view_kw_details"),
    path('tag/<slug:slug>',views.tagged_kw,name="all_tags"),
    path('keywords/tag/<slug:slug>',views.tagged_kw,name="kw_tags"),
    path('brands/',views.brand_list,name="view_all_brands"),
    path('brands/add/', views.BrandCreateView.as_view(), name='create_brand'),
    path('brands/<slug:slug>/details',views.BrandDetailView.as_view(),name="view_brand_details"),
    path('brands/tags/<slug:slug>',views.tagged_brands,name="brand_tags")
]