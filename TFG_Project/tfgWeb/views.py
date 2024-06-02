from django.shortcuts import render
from django.http import JsonResponse
from .models import Pathway, Compound

from .static.scripts.poly_point_isect import *
from .static.scripts.auxiliar_methods import *
import networkx as nx 
import os

import time

def index(request):
  dirname = os.path.dirname(__file__)
  directory = os.path.join(dirname, 'static/inputGraphs')
  filenames = os.listdir(directory)
  filenames.sort()
  
  return render(request, 'index.html', {'filenames': filenames})

def add_pathway(request):
    
   start_time = time.time()

   if request.method == 'POST':
      name = request.POST.get('name')
      pathway = {}
      try:
         pathway = Pathway.objects.get(name=name)    

      except:
         
         G = nx.DiGraph()

         dirname = os.path.dirname(__file__)
         directory = os.path.join(dirname, 'static/inputGraphs', name)
         
         read_graph_from_txt(G, directory)
         
         checkMaxCCSize(G)

         poses = getGraphPositions(G)
         
         graphInfo = parseGraph(G,poses, getCompoundNames(G))

         Pathway.objects.create(name=name, graphInfo = graphInfo)
         
         pathway = Pathway.objects.get(name=name) 


      info = pathway.graphInfo.replace("'", '"')

      end_time = time.time()
      elapsed_time = end_time - start_time
      print("Elapsed time add_pathway: {:.6f} seconds".format(elapsed_time))

      return JsonResponse({'status': 'success', 'graphInfo': info})
   
   return JsonResponse({'status': 'error'})

def getNodeName(label):
   
   try:
      nodeName = Compound.objects.get(pk=label).name
   except:
      nodeName = label
   
   return nodeName

def get_node_info(request):
   if request.method == 'POST':
      start_time = time.time()

      nodeName = request.POST.get('nodeName')
      pathwayName = request.POST.get('pathwayName')
      pathway = Pathway.objects.get(name=pathwayName) 

      G = nx.DiGraph()
      info = pathway.graphInfo.replace("'", '"')
      G = parseJsonToNx(info)

      poses = sugiyama(G)
      pred, succ = getNodeInfo(G,nodeName) 


      predecessors = pred
      successors = succ
      
      if nodeName[0] == 'R':

         predecessors = dict()
         successors = dict()

         for node in pred:
            
            label = getNodeLabel(node)
            nodeName = getNodeName(label)

            predecessors[label] = nodeName
         

         for node in succ:
            label = getNodeLabel(node)
            nodeName = getNodeName(label)
               
            successors[label] = nodeName
      
         predecessors = [f"{key}: {value}" for key, value in predecessors.items()]
         successors = [f"{key}: {value}" for key, value in successors.items()]
      
      label = getNodeLabel(nodeName)
      nodeNameRes = getNodeName(label)
      
      end_time = time.time()
      elapsed_time = end_time - start_time
      print("Elapsed time get_node_info: {:.6f} seconds".format(elapsed_time))

      return JsonResponse({"nodeName":nodeNameRes,'predecessors':predecessors , 'successors': successors})

def get_graph_info(request):
   if request.method == 'POST':
      
      start_time = time.time()

      pathwayName = request.POST.get('pathwayName')
      pathway = Pathway.objects.get(name=pathwayName) 

      G = nx.DiGraph()
      info = pathway.graphInfo.replace("'", '"')
      G = parseJsonToNx(info)

      poses = getGraphPositions(G)
      
      numNodes, numEdges, numCrossings, numCCs, highestDegreeNodes, highestDegree, numNodesCC, avgEdgeLength, angleFactor = getGraphInfo(G, poses) 
      
      highestDegreeNodesResult = {} 

      for node in highestDegreeNodes:
         label = getNodeLabel(node)
         nodeName = getNodeName(label)

         highestDegreeNodesResult[label] = nodeName 

      highestDegreeNodesResult = [f"{key}: {value}" for key, value in highestDegreeNodesResult.items()]
      

      end_time = time.time()
      elapsed_time = end_time - start_time
      print("Elapsed time get_graph_info: {:.6f} seconds".format(elapsed_time))
      
      return JsonResponse({'numNodes': numNodes, 'numEdges': numEdges, 'numCrossings': numCrossings, 'numCCs': numCCs, 'highestDegreeNodes':highestDegreeNodesResult, 'highestDegree': highestDegree, 'numNodesCC':numNodesCC, 'avgEdgeLength': avgEdgeLength, 'angleFactor': angleFactor})


def get_cycles_info(request):
   if request.method == 'POST':
      start_time = time.time()
      
      pathwayName = request.POST.get('pathwayName')
      pathway = Pathway.objects.get(name=pathwayName) 

      G = nx.DiGraph()
      info = pathway.graphInfo.replace("'", '"')
      G = parseJsonToNx(info)

      numCycles, nodeInMostCycles = getCyclesInfo(G)
      
      nodeInMostCyclesLabel = getNodeLabel(nodeInMostCycles)
      nodeInMostCyclesName = getNodeName(nodeInMostCyclesLabel)

      end_time = time.time()
      elapsed_time = end_time - start_time
      print("Elapsed time get_cycles_info: {:.6f} seconds".format(elapsed_time))
      
      return JsonResponse({'numCycles': numCycles, 'nodeInMostCycles': {"id": nodeInMostCycles, "name": nodeInMostCyclesName}})


def split_high_degree(request):
   if request.method == 'POST':
      start_time = time.time()
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

      end_time = time.time()
      elapsed_time = end_time - start_time
      print("Elapsed time split_high_degree: {:.6f} seconds".format(elapsed_time))

      return JsonResponse({'graphInfo':info})

def duplicate_node(request):
   if request.method == 'POST':
      start_time = time.time()
      pathwayName = request.POST.get('name')
      node = request.POST.get('node')
      print(node)
      if node[0] != 'D' :
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


         end_time = time.time()
         elapsed_time = end_time - start_time
         print("Elapsed time duplicate_node: {:.6f} seconds".format(elapsed_time))

         return JsonResponse({'graphInfo':info})
         
      else:
         return JsonResponse({'status': 'error'})
   else:
      return JsonResponse({'status': 'error'})


def getCompoundNames(G):
   start_time = time.time()

   compounds = dict()
   for node in G.nodes():
      if node[0] != 'R':
         # print(getNodeLabel(node))
         label = getNodeLabel(node)
         if not label in compounds:
            try:
               nodeName = Compound.objects.get(pk=label).name
            except:
               nodeName = label
            
         compounds[label] = nodeName
      
   
   end_time = time.time()
   elapsed_time = end_time - start_time
   print("Elapsed time getCompoundNames: {:.6f} seconds".format(elapsed_time))
   
   return compounds

def reset_graph(request):
   if request.method == 'POST':
      start_time = time.time()

      name = request.POST.get('name')
      
      G = nx.DiGraph()

      dirname = os.path.dirname(__file__)
      directory = os.path.join(dirname, 'static/inputGraphs', name)
      read_graph_from_txt(G, directory)
      
      poses = getGraphPositions(G)

      graphInfo = parseGraph(G,poses, getCompoundNames(G))

      pthwy = Pathway.objects.get(pk=name)
      pthwy.graphInfo = graphInfo
      pthwy.save()

      info = pthwy.graphInfo.replace("'", '"')

      end_time = time.time()
      elapsed_time = end_time - start_time
      print("Elapsed time duplicate_node: {:.6f} seconds".format(elapsed_time))
   
      return JsonResponse({'graphInfo':info})
   
def update_compounds(request):
   if request.method == 'POST':
      compounds = retrieveNodeNames()
      for compound in compounds:
         try:
            Compound.objects.create(identifier=compound, name=compounds[compound])
         except:
            Compound.objects.filter(identifier=compound).update(name=compounds[compound])
         
   return JsonResponse({'status': 'success'})

def recompute_positions(request):
   if request.method == 'POST':
      start_time = time.time()

      name = request.POST.get('name')
      
      pathway = Pathway.objects.get(name=name) 
   
      G = nx.DiGraph()
      info = pathway.graphInfo.replace("'", '"')
      G = parseJsonToNx(info)

      poses = getGraphPositions(G)      

      graphInfo = parseGraph(G,poses, getCompoundNames(G))

      pthwy = Pathway.objects.get(pk=name)
      pthwy.graphInfo = graphInfo
      pthwy.save()

      info = pthwy.graphInfo.replace("'", '"')

      end_time = time.time()
      elapsed_time = end_time - start_time
      print("Elapsed time duplicate_node: {:.6f} seconds".format(elapsed_time))

      return JsonResponse({'graphInfo':info})