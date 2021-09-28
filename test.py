from functions import *
from code_repository.import_from_S3 import get_dates
import numpy as np
import matplotlib.pyplot as plt

IS_IN_MASK_PIXEL_VALUE = (0, 0, 0, 255)
X = 7680
Y = 10240
TCI = 'TCI'
BLUE = 'B02'
GREEN = 'B03'
RED = 'B04'
NIR = 'B08'
DATE = '2019-08-09'

# def create_rasters():
#     nir = get_pixels_array(get_tile_path(X, Y, NIR, DATE))
#     red = get_pixels_array(get_tile_path(X, Y, RED, DATE))
#     green = get_pixels_array(get_tile_path(X, Y, GREEN, DATE))
#     blue = get_pixels_array(get_tile_path(X, Y, BLUE, DATE))

#     ndvi = calculate_ndvi(nir, red)
#     gndvi = calculate_gndvi(nir, green)
#     endvi = calculate_endvi(nir, green, blue)

#     mask = generate_mask(X,Y)
#     raster = create_vi_raster(mask,ndvi)
    
#     return raster


## TODO: create the Field Raster images
def save_image(data, path): 
    sizes = np.shape(data)
    height = float(sizes[0])
    width = float(sizes[1])
     
    fig = plt.figure()
    fig.set_size_inches(width/height, 1, forward=False)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
 
    ax.imshow(data)
    plt.savefig(path, dpi = height) 
    plt.close()

def generate_patition_mask(path):
    image = Image.open(path)
    mask = np.array(image)
    return np.all(mask == IS_IN_MASK_PIXEL_VALUE, axis = -1)

# Loop through the fields of interest and create a dictionary with these values.
def generate_field_rasters():
    # dates = get_dates()
    # date = dates[len(dates)-1]
    for field in range(1,23):
        path = f'data/partition-mask/mask-x7680-y10240-{field}.png'
        mask = generate_patition_mask(path)

        nir = get_pixels_array(get_tile_path(X, Y, NIR, DATE))
        red = get_pixels_array(get_tile_path(X, Y, RED, DATE))
        green = get_pixels_array(get_tile_path(X, Y, GREEN, DATE))
        blue = get_pixels_array(get_tile_path(X, Y, BLUE, DATE))

        ndvi = calculate_ndvi(nir, red)
        gndvi = calculate_gndvi(nir, green)
        endvi = calculate_endvi(nir, green, blue)
        savi = calculate_savi(nir, red, 0.5)

        raster_types = ['ndvi', 'gndvi', 'endvi','savi']
        # replace ndvi! with the variable name corresponding to your VI timeseries
        for ras_type in raster_types:
            save_path = f'data/raster/{ras_type}-{field}.png'
            content = None
            if (ras_type=='ndvi'):
                content = ndvi
            elif(ras_type=='gndvi'):
                content = gndvi
            elif (ras_type=='endvi'):
                content = endvi
            else:
                content = savi
            raster = create_vi_raster(mask,content)
            save_image(raster,save_path)

# UNCOMMENT TO GENERATE
generate_field_rasters()






