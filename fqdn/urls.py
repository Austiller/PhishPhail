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
 #   path('keywords/<int:pk>/details/', views.KeyWordDetailView.as_view(), name='view_kw_details'),
 #   path('keywords/<int:pk>/details/', views.KeyWordDetailView.as_view(), name='view_kw_details'),
    path('keywords/<slug:slug>/details',views.kw_detail_view,name="view_kw_details"),
    path('tag/<slug:slug>',views.tagged_kw,name="tagged_kw")
]