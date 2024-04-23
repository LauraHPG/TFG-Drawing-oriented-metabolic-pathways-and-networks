from django.template import loader
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Pathway, Compound
from django.core import serializers

from .static.scripts.poly_point_isect import *
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
          
          poses = getGraphPositions(G)
          
          graphInfo = parseGraph(G,poses, getCompoundNames(G))

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
      
      numNodes, numEdges, numCrossings, numCCs, numCycles, nodeInMostCycles, highestDegree = getGraphInfo(G, poses) 
      
      return JsonResponse({'numNodes': numNodes, 'numEdges': numEdges, 'numCrossings': numCrossings, 'numCCs': numCCs, 'numCycles': numCycles, 'nodeInMostCycles': nodeInMostCycles, 'highestDegree': highestDegree})
  
def split_high_degree(request):
   if request.method == 'POST':
      pathwayName = request.POST.get('name')
      threshhold = int(request.POST.get('threshhold'))
      pathway = Pathway.objects.get(name=pathwayName) 

      G = nx.DiGraph()
      info = pathway.graphInfo.replace("'", '"')
      G = parseJsonToNx(info)

      splitHighDegreeComponents(G,threshhold)

      poses = getGraphPositions(G)      

      graphInfo = parseGraph(G,poses, getCompoundNames(G))

      pthwy = Pathway.objects.get(pk=pathwayName)
      pthwy.graphInfo = graphInfo
      pthwy.save()

      info = pthwy.graphInfo.replace("'", '"')

      return JsonResponse({'graphInfo':info})

def duplicate_node(request):
   if request.method == 'POST':
      pathwayName = request.POST.get('name')
      node = request.POST.get('node')
      pathway = Pathway.objects.get(name=pathwayName) 

      G = nx.DiGraph()
      info = pathway.graphInfo.replace("'", '"')
      G = parseJsonToNx(info)

      duplicateNode(G,node)

      poses = getGraphPositions(G)      

      graphInfo = parseGraph(G,poses, getCompoundNames(G))

      pthwy = Pathway.objects.get(pk=pathwayName)
      pthwy.graphInfo = graphInfo
      pthwy.save()

      info = pthwy.graphInfo.replace("'", '"')

      return JsonResponse({'graphInfo':info})

def getCompoundNames(G):
   compounds = dict()
   for node in G.nodes():
      if node[0] != 'R':
         print(getNodeLabel(node))
         label = getNodeLabel(node)
         try:
            nodeName = Compound.objects.get(pk=label).name
         except:
            nodeName = label
            
         compounds[label] = nodeName
   return compounds

def reset_graph(request):
   if request.method == 'POST':
      name = request.POST.get('name')
      
      G = nx.DiGraph()

      dirname = os.path.dirname(__file__)
      directory = os.path.join(dirname, 'static/data/inputGraphs', name)
      read_graph_from_txt(G, directory)
      
      poses = getGraphPositions(G)

      graphInfo = parseGraph(G,poses, getCompoundNames(G))

      pthwy = Pathway.objects.get(pk=name)
      pthwy.graphInfo = graphInfo
      pthwy.save()

      info = pthwy.graphInfo.replace("'", '"')

      return JsonResponse({'graphInfo':info})
   
def update_compounds(request):
   if request.method == 'POST':
      compounds = retrieveNodeNames()
      for compound in compounds:
         Compound.objects.get_or_create(identifier=compound, name=compounds[compound])
   return JsonResponse({'status': 'success'})