from django.urls import path
from . import views
from django.urls import include

from .views import FQDNInstanceListView, kw_detail_view, refresh_brands 

urlpatterns = [
    path('',FQDNInstanceListView.as_view(),name='found_fqdn'),
    path('<int:pk>/details/', views.FQDNInstanceDetails.as_view(), name='view_fqdn_details'),
    path('keywords/',views.keyword_list,name="view_all_keywords"),
    path('keywords/<slug:slug>/details',views.kw_detail_view,name="view_kw_details"),
    path('tag/<slug:slug>',views.tagged_kw,name="all_tags"),
    path('keywords/tags/<slug:slug>',views.tagged_kw,name="kw_tags"),
    path('brands/',views.brand_list,name="view_all_brands"),
    path('brands/refresh',views.refresh_brands,name="refresh_brands"),
    path('brands/<slug:slug>/details',views.brand_detail,name="view_brand_details"),
    path('brands/tags/<slug:slug>',views.tagged_brands,name="brand_tags")
]