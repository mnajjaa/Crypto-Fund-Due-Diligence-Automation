from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
import io
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
from django.utils.decorators import method_decorator
  
def pptx_view(request):
    return render(request, 'pptx_view.html')
