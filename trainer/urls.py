from django.urls import path
from trainer import views
from django.urls import include


urlpatterns = [
    path('create/',views.ModelCreateView.as_view(), name='createModel'),

    path('update_training_data/', views.updateTrainingData, name='update_training_data'),
    path('update_training_data/brands/upload', views.updateTrainingData, name='update_brands'),
    path('update_training_data/keywords/upload', views.updateTrainingData, name='upload_keywords'),
    path('update_training_data/squatedwords/upload', views.updateTrainingData, name='update_squatedwords'),
    path('update_training_data/fqdn/upload', views.updateTrainingData, name='update_fqdn')
]