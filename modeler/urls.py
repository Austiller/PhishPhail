from django.urls import path
from . import views
from django.urls import include


urlpatterns = [
    
    path('<int:pk>/start/',views.startModel, name='start_certstream_task'),
    path('<int:pk>/stop/',views.stopModel, name='stopModel')
]