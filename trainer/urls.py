from django.urls import path
from . import views
from django.urls import include


urlpatterns = [
    path('',views.ModelListView.as_view(), name='models'),
    path('create/',views.ModelCreateView.as_view(), name='createModel'),
    path('<int:pk>/edit/', views.ModelEdit.as_view(), name='modelEdit'),
    path('<int:pk>/details/',views.ModelDetails.as_view(), name='view_model_details'),
    path('trainerSettings',views.trainerSettings, name='trainerSettings')


  
]