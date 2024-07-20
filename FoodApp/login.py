from django.shortcuts import render
from configuration import *


def index(request):
    try:
        return render(request, 'index.html')
    except Exception as e:
        log.error("Exception in Index. Reason : %s" %e)