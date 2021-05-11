from django.urls import path
from . import views
from django.urls import include
from trainer.views import FQDNInstanceDetails
from .views import FQDNInstanceListView 

urlpatterns = [
    path('',FQDNInstanceListView.as_view(),name='found_fqdn'),
    path('<int:pk>/details/', FQDNInstanceDetails.as_view(), name='view_fqdn_details'),
    path('keywords/',views.KeyWordListView.as_view(),name="view_all_keywords")
    

]