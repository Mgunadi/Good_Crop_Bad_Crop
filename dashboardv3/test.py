from PIL import Image
from matplotlib import image
import os
#print(os.getcwd())

def get_tile_path(x, y, band, date):
    path = f'C:\\Users\\Gladiator\\Documents\\Good_Crop_Bad_Crop\\model\\satelite_data\\phase-01\\data\\sentinel-2a-tile-{x}x-{y}y\\timeseries\\{x}-{y}-{band}-{date}.png'
    return path

def get_image(x, y, band, date):
    path = get_tile_path(x,y,band,date)
    im = image.imread(path)
    return im

#print(get_image('7680', '10240', 'B01', '2016-12-22'))
