from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse

from PIL import Image
import numpy as np
import base64
from io import BytesIO


def index(request):
	image = process_image()
	return render(request, 'crop/home.html')


def process_image():
	img_path = settings.IMG_URL / 'sentinel-2a-tile-7680x-10240y/timeseries/7680-10240-TCI-2016-12-22.png'
	mask_path = settings.IMG_URL / 'sentinel-2a-tile-7680x-10240y/masks/sugarcane-region-mask.png'
	# print(img_path)
	with Image.open(img_path) as im1:
		im2 = im1.copy()
		img_pixels = im2.load()

	with Image.open(mask_path) as maskim1:
		mask_pixels = maskim1.load()  

	
	for x in range(0,512):
		for y in range(0,512):
			print(mask_pixels[x,y])
			if mask_pixels[x,y] != (0,0,0,255):
				img_pixels[x,y] = (0,0,0)


	# buffer = BytesIO()
	im2.save(str(settings.MEDIA_PATH )+'/result1.png',format="PNG")
	# myimage = buffer.getvalue()   
	# b64_string = base64.b64encode(myimage).decode('ascii')
