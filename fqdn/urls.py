from django.urls import path
from . import views
from django.urls import include



urlpatterns = [
    path('',views.FQDNInstanceListView.as_view(),name='found_fqdn'),

    path('fqdn/forTraining',views.json_all,name="json_all"),
    path('fqdn/csv_all',views.csv_all,name="csv_all"),
    path('fqdn/csv_maliicious',views.csv_malicious,name="csv_malicious"),
    path('<int:pk>/details/', views.FQDNInstanceDetails.as_view(), name='view_fqdn_details'),
    path('<str:attribute_name>/',views.attribute_list,name="attribute_list"),
    path('<str:attribute_name>/<slug:slug>/details',views.attribute_detail,name="attribute_details"),
    path('<str:attribute_name>/tags/<slug:slug>',views.attribute_tags,name="attribute_tags"),
 
    path('brands/refresh',views.refresh_brands,name="refresh_brands"),

]