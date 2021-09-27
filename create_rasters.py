from functions import *

def create_rasters():
    nir = get_pixels_array(get_tile_path(X, Y, NIR, DATE))
    red = get_pixels_array(get_tile_path(X, Y, RED, DATE))
    green = get_pixels_array(get_tile_path(X, Y, GREEN, DATE))
    blue = get_pixels_array(get_tile_path(X, Y, BLUE, DATE))

    ndvi = calculate_ndvi(nir, red)
    gndvi = calculate_gndvi(nir, green)
    endvi = calculate_endvi(nir, green, blue)

    mask = generate_mask(X,Y)
    raster = create_vi_raster(mask,ndvi)
    
    return raster


#plt.imshow(raster)