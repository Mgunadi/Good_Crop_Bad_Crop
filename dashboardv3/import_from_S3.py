import boto3
import glob

# Set up import paths
s3 = boto3.resource('s3')
BUCKET_NAME = 'goodcropbadcrop'
KEY = 'satellite-data/phase-01/data/sentinel-2a-tile-7680x-10240y/timeseries/7680-10240-TCI-2019-08-09.png'


# Front End Imports
# Outputs satellite image file to current directory
s3.Bucket(BUCKET_NAME).download_file(KEY, 'current_satellite_image.jpg')


# Back End Imports
# TODO: Convert this absolute path import statement to an S3.Bucket call
# Outputs vegetation index list (using glob)
def get_tile_path(x, y, band, date):
    path = f'C:\\Users\\Gladiator\\Documents\\Good_Crop_Bad_Crop\\model\\satelite_data\\phase-01\\data\\sentinel-2a-tile-{x}x-{y}y\\timeseries\\{x}-{y}-{band}-{date}.png'
    return path

def get_path_list():    
    paths = glob.glob(get_tile_path('7680','10240','B01','*'))
    return paths

