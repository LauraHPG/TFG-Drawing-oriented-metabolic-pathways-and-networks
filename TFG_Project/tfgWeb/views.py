from django.template import loader
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Pathway

from .static.scripts.auxiliar_methods import *
import networkx as nx 
import os

def index(request):
  dirname = os.path.dirname(__file__)
  directory = os.path.join(dirname, 'static/data/inputGraphs')
  filenames = os.listdir(directory)
  filenames.sort()
  
  return render(request, 'index.html', {'filenames': filenames})

def add_pathway(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        pathway = {}
        try:

          G = nx.DiGraph()

          dirname = os.path.dirname(__file__)
          directory = os.path.join(dirname, 'static/data/inputGraphs', name)
          read_graph_from_txt(G, directory)
          
          changeSourceAndSinkNodeType(G)
          setColorNodeType(G)
          poses = sugiyama(G)
          
          graphInfo = parseGraph(G,poses)

          Pathway.objects.create(name=name, graphInfo = graphInfo)
          
          pathway = Pathway.objects.get(name=name) 

        except:
          pathway = Pathway.objects.get(name=name)    

        info = pathway.graphInfo.replace("'", '"')
        return JsonResponse({'status': 'success', 'graphInfo': info})
    
    return JsonResponse({'status': 'error'})

def get_node_info(request):
   if request.method == 'POST':
      nodeName = request.POST.get('nodeName')
      pathwayName = request.POST.get('pathwayName')
      pathway = Pathway.objects.get(name=pathwayName) 

      G = nx.DiGraph()
      info = pathway.graphInfo.replace("'", '"')
      G = parseJsonToNx(info)

      poses = sugiyama(G)
      pred, succ = getNodeInfo(G,nodeName) 
      
      return JsonResponse({'predecessors': pred, 'successors': succ})


def get_graph_info(request):
   if request.method == 'POST':
      pathwayName = request.POST.get('pathwayName')
      pathway = Pathway.objects.get(name=pathwayName) 

      G = nx.DiGraph()
      info = pathway.graphInfo.replace("'", '"')
      G = parseJsonToNx(info)

      poses = sugiyama(G)
      numNodes, numEdges, numCrossings, numCCs = getGraphInfo(G, poses) 
      
      return JsonResponse({'numNodes': numNodes, 'numEdges': numEdges, 'numCrossings': numCrossings, 'numCCs': numCCs})