import numpy as np
import folium
import glob
import json
import os
#import rasterio as rio
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib import cm
from folium.plugins import HeatMap
from PIL import Image


# Constants 
API_KEY = 'pk.eyJ1Ijoia25lZGxpa3kiLCJhIjoiY2t0NzN4OXg4MG9ueDJvcndoM3R3bjFvayJ9.y06YZbRFunBbKyD8HuKTlw'
PATH = os.path.join(os.getcwd(), 'data')
X = 7680
Y = 10240
TCI = 'TCI'
BLUE = 'B02'
GREEN = 'B03'
RED = 'B04'
NIR = 'B08'
DATE = '2019-08-09'
TILE_WIDTH_PX = 512
TILE_HEIGHT_PX = 512
IS_IN_MASK_PIXEL_VALUE = (0, 0, 0, 255)



# get tile path
def get_tile_path(lat, lon, band, date):
    path = f'{PATH}/timeseries/{lat}-{lon}-{band}-{date}.png'
    return path


# get png mask path
def get_mask_path(lat, lon):
    path = f'{PATH}/masks/mask-x{lat}-y{lon}.png'
    return path


# get image as a PNG image file
def get_tile(tile_path):
    image = Image.open(tile_path)
    return image


# get mask as a PNG image file
def get_mask(mask_path):
    image = Image.open(mask_path)
    return image


# open image file and returns pixel object
def get_pixels(tile_path):
    image = Image.open(tile_path)
    pixels = image.load()
    return pixels


# returns an image as a numpy array
def get_pixels_array(tile_path):
    image = Image.open(tile_path)
    return np.array(image)


# creates an image from a numpy array
def create_image(np_array):
    return Image.fromarray(np_array)


# returns the south-east and north west corner of a tile
def get_bounds(lat, lon):
    with open(f'{PATH}/geometries/geo-x{lat}-y{lon}.geojson') as f:
        coordinates = json.load(f)['features'][0]['geometry']['coordinates']
        lon_min = coordinates[0][1][0]
        lat_min = coordinates[0][1][1]
        lon_max = coordinates[0][3][0]
        lat_max = coordinates[0][3][1]
        return [[lat_min, lon_min], [lat_max, lon_max]]


# returns an area of interest as a GeoPandas object
def get_aoi(lat, lon):
    return gpd.read_file(f'{PATH}/geometries/geo-x{lat}-y{lon}.geojson')
    
    
# returns the centroid of an area, in the form (lon, lat)
def get_centroid(lat, lon):
    [[x1, y1], [x2, y2]] = get_bounds(lat, lon)
    return [(x1 + x2)/ 2, (y1 + y2) / 2]


# returns a mask
def is_in_mask(mask_pixels, pixel_x, pixel_y):
    if mask_pixels[pixel_y, pixel_x] == IS_IN_MASK_PIXEL_VALUE:
        return True
    else:
        return False
    
    
# creates a mask to create a transparent layer for the VIs on each tile
def generate_mask(lat,lon):
    mask = get_pixels_array(get_mask_path(lat,lon))
    return np.all(mask == IS_IN_MASK_PIXEL_VALUE, axis = -1)


# returns a masked array    
def create_masked_raster(array, mask):
    return np.ma.MaskedArray(array, mask)


### NDVI calculations

# vegetation index calculations
def calculate_ndvi(NIR, RED):
    return (NIR - RED) / (NIR + RED)


def calculate_gndvi(NIR, GREEN):
    return (NIR - GREEN) / (NIR + GREEN)


def calculate_endvi(NIR, GREEN, BLUE):
    return ((NIR + GREEN) - (2 * BLUE)) / ((NIR + GREEN) + (2 * BLUE)) 

def calculate_savi(NIR, RED, L):
    return (NIR - RED) / (NIR + RED + L) * (1+L)


# create a masked raster image based on a vegetation index
def create_vi_raster(mask, vi):
    minima = np.min(vi)
    maxima = np.max(vi)

    norm = Normalize(vmin = minima, vmax = maxima, clip = True)
    mapper = cm.ScalarMappable(norm = norm, cmap = cm.viridis)

    rgb = mapper.to_rgba(vi)
    rgb[~mask] = [0,0,0,0]

    return rgb
