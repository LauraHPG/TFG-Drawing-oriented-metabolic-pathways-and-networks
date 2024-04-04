from django.template import loader
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Pathway
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
        Pathway.objects.create(name=name)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})