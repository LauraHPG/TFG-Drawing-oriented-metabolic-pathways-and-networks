from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add_pathway/', views.add_pathway, name='add_pathway'),   
    path('get_node_info/', views.get_node_info, name='get_node_info'),  
    path('get_graph_info/', views.get_graph_info, name='get_graph_info')   
    # path('tfgWeb/', views.index, name='index'),
]
