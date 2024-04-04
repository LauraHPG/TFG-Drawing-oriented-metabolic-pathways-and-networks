from django.shortcuts import render
from .models import PathwayInfo
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

import os
# import static.scripts.main

def index(request):
    directory = '/home/laura/Documents/TFG-Drawing-oriented-metabolic-pathways-and-networks/tfgWeb/tfgWeb/static/data/inputGraphs'
    filenames = os.listdir(directory)
    filenames.sort()

    if request.method == 'POST' and 'run_script' in request.POST:
        
        print("clicked")
    
    return render(request, 'index.html', {'filenames': filenames})

def add_pathway(request):
    if request.method == 'POST':
        name = request.POST.get('pathwaysList')
        print(request.POST['pathwayNames'])
        PathwayInfo.objects.create(name=name)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})