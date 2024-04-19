from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('update_compounds/', views.update_compounds, name='update_compounds'), 
    path('add_pathway/', views.add_pathway, name='add_pathway'),   
    path('get_node_info/', views.get_node_info, name='get_node_info'),  
    path('get_graph_info/', views.get_graph_info, name='get_graph_info'),   
    path('split_high_degree/', views.split_high_degree, name='split_high_degree'), 
    path('duplicate_node/', views.duplicate_node, name='duplicate_node'), 
    path('reset_graph/', views.reset_graph, name='reset_graph')   
    # path('tfgWeb/', views.index, name='index'),
]
