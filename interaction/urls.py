from rest_framework import routers
from django.urls import path
from . import views

urlpatterns = [path('list_interaction/', views.GetInteractionOfProduct.as_view(), name='List Interaction')]
