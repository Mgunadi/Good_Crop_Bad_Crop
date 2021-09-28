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


## TODO: create the Field Raster images
def save_image(data): 
    sizes = np.shape(data)
    height = float(sizes[0])
    width = float(sizes[1])
     
    fig = plt.figure()
    fig.set_size_inches(width/height, 1, forward=False)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
 
    ax.imshow(data)
    plt.savefig('Partition1', dpi = height) 
    plt.close()

# Loop through the fields of interest and create a dictionary with these values.
def create_field_rasters():
    field_dict = {}
    for field in [1,2,12]:
        path = f'data\\partition-mask\\mask-x7680-y10240-{field}.png'
        im = Image.open(path)
        field_dict[f'mask_{field}'] = im

    for mask in field_dict.values:
        # replace ndvi! with the variable name corresponding to your VI timeseries
        raster = create_vi_raster(mask,ndvi1)
        save_image(raster)



