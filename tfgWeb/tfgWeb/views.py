from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
import os
# import static.scripts.main

def index(request):
    directory = '/home/laura/Documents/TFG-Drawing-oriented-metabolic-pathways-and-networks/tfgWeb/tfgWeb/static/data/inputGraphs'
    filenames = os.listdir(directory)
    filenames.sort()

    if request.method == 'POST' and 'run_script' in request.POST:
        
        print("clicked")
    
    return render(request, 'index.html', {'filenames': filenames})