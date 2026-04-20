from django.urls import path
from . import views

urlpatterns = [
    path('', views.pieteikumu_saraksts, name='saraksts'),
    path('jauns/', views.jauns, name='jauns'),
    path('rediget/<int:id>/', views.rediget, name='rediget'),
    path('dzest/<int:id>/', views.dzest, name='dzest'),
    path('register/', views.registracija, name='register'),
]