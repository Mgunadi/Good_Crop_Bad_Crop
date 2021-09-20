import boto3
import glob

# Set up import paths
s3 = boto3.resource('s3')
BUCKET_NAME = 'goodcropbadcrop'
KEY = 'satellite-data/phase-01/data/sentinel-2a-tile-7680x-10240y/timeseries/7680-10240-TCI-2019-08-09.png'
DATES_KEY = 'satellite-data/phase-01/data/sentinel-2a-tile-7680x-10240y/timeseries/7680-10240-B01-'

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

# old function to get dates
# def get_dates():
#     dates = []
#     for obj in bucket.objects.filter(Prefix=DATES_KEY):
#         content = obj.key
#         x = len(content)
#         date = content[x-14:x-4]
#         dates.append(date)
#     dates.sort(key= lambda x: int(''.join(x.split('-'))))
#     return dates

# return custom key for s3
def get_s3_KEY(x,y, band, date):
    CUSTOM_KEY = f'satellite-data/phase-01/data/sentinel-2a-tile-{x}x-{y}y/timeseries/{x}-{y}-{band}-{date}.png'
    return CUSTOM_KEY

# NEED MODIFICATION FOR FUTURE USE, DO NOT REMOVE THIS COMMENT
# This function return a list of sorted dates
def get_dates():
    dates = []
    for obj in bucket.objects.filter(Prefix=DATES_KEY):
        content = obj.key
        x = len(content)
        date = content[x-14:x-4]
        dates.append(date)
    dates.sort(key= lambda x: int(''.join(x.split('-'))))
    return dates

# function to an array of wavelength value
def get_wavelength(x, y, band, date)
    custom_key = get_s3_KEY(x,y, band, date)
    pic_bytes = s3.Object(BUCKET_NAME, custom_key).get()['Body'].read()
    im = Image.open(io.BytesIO(pic_bytes))
    arr = np.array(im.getdata()).reshape(512,512)
    return arr

