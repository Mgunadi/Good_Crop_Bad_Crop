import json
import os
from os import listdir
from os.path import isfile, join, abspath
from math import sin, cos, sqrt, atan2, radians


current_dir = abspath(os.getcwd()) + '/data/rainfall/'
geojson_dir = abspath(os.getcwd()) +"/../satelite_data/Phase02-DataDelivery/geometries/"
onlyfiles = [f for f in listdir(current_dir) if isfile(join(current_dir, f))]
geom_files = [f for f in listdir(geojson_dir) if isfile(join(geojson_dir, f))]

def calculate_distance(latitude1, longitude1, latitude2, longitude2):
	# approximate radius of earth in km
	radius = 6373.0
	lat1 = radians(latitude1)
	lon1 = radians(longitude1)
	lat2 = radians(latitude2)
	lon2 = radians(longitude2)

	dlon = lon2 - lon1
	dlat = lat2 - lat1

	a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
	c = 2 * atan2(sqrt(a), sqrt(1 - a))

	distance = radius * c

	return distance



# for file in onlyfiles:
#     f = open(current_dir+"/"+file)
#     json_file = json.load(f)
#     a = len(json_file['col'])
#     if x == True:
#         print(json_file['col'])
#         x =False
#     print(a)



for g_file in geom_files:
	f = open(geojson_dir+"/"+g_file)
	geo_file = json.load(f)
	coordinates = geo_file['features'][0]['geometry']['coordinates'][0]
	min_distance = 1000000000
	station = ''
	min_lat = 0 
	min_long = 0 
	for coordinate in coordinates:
		longitude1 = round(coordinate[0],2)
		latitude1 = round(coordinate[1],2)

		for x_file in onlyfiles:
			f = open(current_dir+"/"+x_file)
			json_file = json.load(f)
			latitude2 = float(json_file['latitude'])*-1
			longitude2 = float(json_file['longitude'])

			distance = calculate_distance(latitude1, longitude1, latitude2, longitude2)

			if (distance < min_distance):
				min_distance = distance
				station = x_file
				min_lat = latitude2 - latitude1
				min_long = longitude2 - longitude1
	print(g_file+" "+station+" "+str(min_distance)+" km")

	
# print(geom_files)
