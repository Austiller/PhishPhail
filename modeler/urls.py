from django.urls import path
from . import views
from django.urls import include
from trainer.views import ModelListView

urlpatterns = [
    path('',ModelListView.as_view(),name='models'),
    path('<int:pk>/edit/',views.ModelEdit.as_view(),name='modelEdit'),
    path('<int:pk>/delete/',views.ModelDeleteView.as_view(),name='delete_model'),
    path('<int:pk>/start/',views.startModel, name='start_certstream_task'),
    path('<int:pk>/stop/',views.stopModel, name='stopModel'),
    path('download/All/',views.csvAll,name='download_all'),
    path('download/Malicious/',views.csvMalicious,name='download_malicious')

]