from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add_pathway/', views.add_pathway, name='add_pathway')    
    # path('tfgWeb/', views.index, name='index'),
]
