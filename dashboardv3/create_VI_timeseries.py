import pandas as pd
import numpy as np
from PIL import Image
from matplotlib import image
import glob
from import_from_S3 import get_tile_path, get_path_list
from callback_functions import get_crop_mask

# Code the colour bands
BLUE = 'B02'
GREEN = 'B03'
RED = 'B04'
NIR = 'B08'

VI_dict = {}

# Function that gets specific image - not currently called upon
def get_image(x, y, band, date):
    path = get_tile_path(x,y,band,date)
    im = image.imread(path)
    return im

# NVDI calculation
def calculate_NVDI(NIR, RED):
    return (NIR - RED) / (NIR + RED)

# ENVDI calcuation
def calculate_ENVDI(NIR, GREEN, BLUE):
    return ((NIR+GREEN) - (2*BLUE)) / ((NIR+GREEN) + (2*BLUE)) 

# GNDVI calcuation
def calulcate_GNDVI(NIR, GREEN):
    return (NIR - GREEN) / (NIR + GREEN)

def get_wavelength(x, y, band, date):
    im = Image.open(get_tile_path(x,y,band,date))
    arr = np.array(im.getdata()).reshape(512,512)
    return arr

def get_partition(image, xStart, yStart, mask):
    result = [] 
    for y in range(0, len(mask)):
        for x in range(0, len(mask[0])):
            # check if the mask pixel is selected then add the img pixel to list
            if mask[y,x]==1:
                result.append(image[yStart+y, xStart+x])
    return np.array(result)


def get_avg_vegetation_index(vi, X, Y, xStart, yStart, mask, date_range):
    paths = glob.glob(get_tile_path('7680','10240','B01','*'))
    # print(type(paths))
    date_range = []
    result = []
    avg = []
    upper = []
    lower = []
    dates = []

    # Create list of dates
    for path in paths:
        x = len(path)
        dates.append(path[x-14:x-4])
    
    # sort the list of dates  
    dates.sort(key= lambda x: int(''.join(x.split('-'))))

    for date in dates[0:12]:
        red = get_wavelength(X,Y,RED,date)
        blue = get_wavelength(X,Y,BLUE,date)
        green = get_wavelength(X,Y,GREEN,date)
        nir = get_wavelength(X,Y,NIR,date)
        
        # TODO: extend to all VI's
        if vi == 'NVDI':
            nvdi = calculate_NVDI(nir, red)
            res = get_partition(nvdi, xStart, yStart, mask)
            average = np.average(res)
            sd = np.std(res)

            avg.append(average)
            upper.append(average+(2*sd))
            lower.append(average-(2*sd))
            result.append(res)
    dict = {}
    dict['result'] = result
    dict['avg'] = avg
    dict['upper'] = upper
    dict['lower'] = lower
    return dict


# Create dataframe for the VI time series graphs
def create_NVDI_dataframe():
    # Create time series of vegetation index
    xlabels = [] 
    result = []
    xlabel2 = []
    X = '7680'
    Y = '10240'
    xStart = 0
    yStart = 0
    # TODO: Create callback function that generates mask when a polygon section of the satellite image is selected
    # mask = get_crop_mask()
    mask = np.ones((20,20))
    temp = get_avg_vegetation_index('NVDI', X, Y, xStart, yStart, mask, 2)

    for i in range(0, len(temp['result'])):
        xlabel2.append(i)
        for res in temp['result'][i]:
            result.append(res)
            xlabels.append(i)
    
    df = pd.DataFrame({'Stage': xlabel2, 'Average': temp['avg'], 'Upper': temp['upper'], 'Lower': temp['lower']})
    VI_dict['NDVI'] = df 
    #print(VI_dict['NDVI'])


# TODO: Create a dictionary for dataframes of different VIs using a for loop
#  not just a dataframe for NDVI, 
def create_VI():
    create_NVDI_dataframe()
    return VI_dict

