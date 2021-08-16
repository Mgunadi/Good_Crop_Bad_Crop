from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from io import BytesIO
from PIL import Image
import base64
import geopandas
import matplotlib.pyplot as plt
import numpy as np


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
	print(im2.size)


	with Image.open(mask_path) as maskim1:
		mask_pixels = maskim1.load()  
	print(maskim1.size)
	
	# FILTER USING MASK
	# color_list = []
	# for x in range(0,512):
	# 	for y in range(0,512):
	# 		# print(mask_pixels[x,y])
	# 		if mask_pixels[x,y] != (0,0,0,255):
	# 			if x-50 >= 0:
	# 				if y-5 >= 0:
	# 					color_list.append(img_pixels[x-50,y-5])
	# 					# img_pixels[x-50,y-5] = (0,0,0)
	#       
	#FILTER OTHER EXCEPT THE MASK
	# 		else:
	# 			if x-50 >= 0:
	# 				if y-5 >= 0:
	# 					img_pixels[x-50,y-4] = (0,0,0)
	#
	#
	# FIND AVERAGE AND FILTER USNG AVERAGE +- RANGE
	# a, b, c = 0, 0, 0
	# for col in color_list:
	# 	d, e, f = col
	# 	a+=d
	# 	b+=e
	# 	c+=f
	# a /= len(color_list)
	# b /= len(color_list)
	# c /= len(color_list)

	# print(a)
	# print(b)
	# print(c)
	# for x in range(0,512):
	# 	for y in range(0,512):
	# 		if img_pixels[x,y] != (0,0,0):
	# 			d, e, f = img_pixels[x,y]
	# 			# compare with average with range
	# 			g = 30
	# 			if (d >= a-g and d <= a+g) and (e >= b-g and e <= b+g) and (f >= c-g and f <= c+g ):
	# 			# if (a >= 74) and (b>= 80) and (c >= 80): 
	# 				img_pixels[x,y] = (255,255,0) 
	#
	# COLOR SEPERATOR ONLY RED GREEN BLUE OR COMBINE
	# for x in range(0,512):
	#  	for y in range(0,512):
	#  		if img_pixels[x,y] != (0,0,0):
	#  			d, e, f = img_pixels[x,y]
	#  			img_pixels[x,y] = (0,e,0)
	#
	#
	#
	# buffer = BytesIO()
	im2.save(str(settings.MEDIA_PATH )+'/result10.png',format="PNG")
	# myimage = buffer.getvalue()   
	# b64_string = base64.b64encode(myimage).decode('ascii')

def generate_mask_from_geojson(requrest):
	# geojson_file_path = settings.IMG_URL / 'sentinel-2a-tile-7680x-10240y/geometry/file-x7680-y10240.geojson'
	# temp = geopandas.read_file(geojson_file_path)
	# temp.plot()
	# print(settings.STATIC_URL)
	# path = settings.STATIC_PATH / 'media/'
	# name = 'result3.png'
	# plt.savefig(str(path)+name)
	# print(temp.head())
	return HttpResponse("Success")