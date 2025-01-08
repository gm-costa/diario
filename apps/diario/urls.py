from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='diario'),
    path('escrever/', views.escrever, name='escrever'),
]