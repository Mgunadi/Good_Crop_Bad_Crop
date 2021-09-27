
from PIL import Image
import numpy as np
import os

# Set up import paths


DATA_PATH = os.path.join(os.getcwd(), '../data/')

def get_image(x, y, date):
    path = f'{DATA_PATH}/timeseries/{x}-{y}-TCI-{date}.png'
    im = Image.open(path)
    arr = np.array(im.getdata()).reshape(512,512,3)
    return arr


# This function get the mask
def get_mask_partition(x, y, idx):
    mask_path = f'{DATA_PATH}/partition-mask/mask-x{x}-y{y}-{idx}.png'
    im = Image.open(mask_path)
    arr = np.array(im.getdata()).reshape(512,512,4)
    return arr

def get_mask(x, y):
    mask_path = f'{DATA_PATH}/masks/mask-x{x}-y{y}.png'
    im = Image.open(mask_path)
    arr = np.array(im.getdata()).reshape(512,512,4)
    return arr


# function to an array of wavelength value
def get_wavelength(x, y, band, date):
    path = f'{DATA_PATH}/timeseries/{x}-{y}-{band}-{date}.png'
    im = Image.open(path)
    arr = np.array(im.getdata()).reshape(512,512)
    return arr

