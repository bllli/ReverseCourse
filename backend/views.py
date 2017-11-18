import json

from django.http import HttpResponse
from django.shortcuts import render

from .models import Article


def base(request):
    return render(request, 'base.html')


def index(request):
    data = list(Article.objects.values('title'))
    # return HttpResponse(json.dumps(data), content_type='application/json')
    return render(request, 'index.html')
