from django.template import loader
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Pathway
from .static.scripts.auxiliar_methods import read_graph
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
        print(name)
        try:
          Pathway.objects.create(name=name)
        except:
          pathway = Pathway.objects.get(name=name)    
          print(pathway)      
          return JsonResponse({'status': 'error'})
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})