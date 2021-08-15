from django.shortcuts import render
from django.conf import settings


# Create your views here.
from django.http import HttpResponse


def index(request):
	print(settings.IMG_URL)
	return render(request, 'crop/home.html')