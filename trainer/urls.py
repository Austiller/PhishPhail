from django.urls import path
from . import views
from django.urls import include


urlpatterns = [
 
    path('create/',views.ModelCreateView.as_view(), name='createModel'),
    path('<int:pk>/details/', views.fqdninstance_details, name='view_fqdn_details'),
    path('update_training_data/', views.updateTrainingData, name='update_training_data'),
    path('update_training_data/brands/', views.updateTrainingData, name='update_brands'),
    path('update_training_data/keywords/', views.updateTrainingData, name='update_keywords'),
    path('update_training_data/squatedwords/', views.updateTrainingData, name='update_squatedwords'),
    path('update_training_data/fqdn/', views.updateTrainingData, name='update_fqdn')
]