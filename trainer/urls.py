from django.urls import path
from . import views
from django.urls import include


urlpatterns = [
 
    path('create/',views.ModelCreateView.as_view(), name='createModel'),
    path('<int:pk>/details/', views.fqdninstance_details, name='view_fqdn_details'),
    


  
]