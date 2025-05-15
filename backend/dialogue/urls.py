from django.urls import path
from . import views

urlpatterns = [
    path('dialogueLocalModel', views.dialogueLocalModel, name='dialogue_local_model'),
]