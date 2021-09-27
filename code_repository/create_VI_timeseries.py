import pandas as pd
import numpy as np
from PIL import Image
from matplotlib import image
from import_from_S3 import get_dates
from import_from_local import get_mask, get_wavelength, get_image, get_mask_partition
import statistics
import os
import sys
import numpy.ma as ma

sys.setrecursionlimit(10**6)


# Code the colour bands
BLUE = 'B02'
GREEN = 'B03'
RED = 'B04'
NIR = 'B08'

# Create a dictionary for the VI's
VI_dict = {}


# SAVI calculation
def calculate_SAVI(NIR, RED, L):
    return (NIR - RED) / (NIR + RED + L) * (1+L)

# NDVI calculation
def calculate_NDVI(NIR, RED):
    return (NIR - RED) / (NIR + RED) 

# ENDVI calcuation
def calculate_ENDVI(NIR, GREEN, BLUE):
    return ((NIR+GREEN) - (2*BLUE)) / ((NIR+GREEN) + (2*BLUE)) 

# GNDVI calcuation
def calculcate_GNDVI(NIR, GREEN):
    return (NIR - GREEN) / (NIR + GREEN)

def split_mask(X,Y):
    # print(os.getcwd())
    mask = get_mask(X, Y)
    split_mask = []
    for i in range(0,512):
        row = []
        for j in range(0,512):
            row.append(-1)
        split_mask.append(row)

    count = 1
    for i in range(0,512):
        for j in range(0,512):
            if (split_mask[i][j]==-1):
                if(mask[i,j,3]==255):
                    bfs(i,j,i,j,mask, split_mask, count, 0)
                    count+=1
                else:
                    split_mask[i][j] = 0
    total = 0
    number = 1

    for x in range(1,count):
        mask = get_mask(X, Y)
        arr = np.array(split_mask)
        total = 0
        for i in range(0,512):
            for j in range(0,512):
                if split_mask[i][j] !=x:
                    mask[i,j,3] = 0
                else:
                    total +=1
        if (total > 100):
            data = mask.astype(np.uint8)
            img = Image.fromarray(data, 'RGBA') 
            filename = f'../data/partition-mask/mask-x{X}-y{Y}-{number}.png'
            number+=1
            path = os.path.join(os.getcwd(), filename)
            print(path)
            img.save(path)




def bfs(i,j, i_prev, j_prev, mask, split_mask, idx, dept):
    if i>=0 and i <=511 and j>=0 and j<=511:
        if mask[i,j,3] == 255 and split_mask[i][j]==-1:
            split_mask[i][j] = idx
            i1 = i-1
            i2 = i+1
            j1 = j-1
            j2 = j+1
            temp = dept + 1
            if (temp < 45000):
                if i2<512 and (i2 != i_prev or j != j_prev) and mask[i2,j,3] == 255 and split_mask[i2][j]==-1:
                    temp = temp+1
                    bfs(i2,j, i,j, mask, split_mask, idx, temp)
                if j1>=0 and (i != i or j1 != j_prev) and mask[i,j1,3] == 255 and split_mask[i][j1]==-1:
                    temp = temp+1
                    bfs(i,j1, i,j, mask, split_mask, idx, temp)
                if i1>=0 and (i1 != i_prev or j != j_prev) and mask[i1,j,3] == 255 and split_mask[i1][j]==-1:
                    temp = temp+1
                    bfs(i1,j, i,j, mask, split_mask, idx, temp)
                if j2<512 and (i != i or j2 != j_prev) and mask[i,j2,3] == 255 and split_mask[i][j2]==-1:
                    temp = temp+1
                    bfs(i,j2, i,j, mask, split_mask, idx, temp)


# UNCOMMENT THIS TO GENERATE PARTITION MASK
# split_mask('7680', '10240')

def generate_VI_timeseries_DF(X,Y, path):
    dates = get_dates()

    for j in range(1,23):
        result = {}

        result['date'] = []

        result[BLUE] = []
        result[GREEN] = []
        result[RED] = []
        result[NIR] = []
        result['NDVI'] = []
        result['SAVI'] = []
        result['ENDVI'] = []
        result['GNDVI'] = []

        result['B02_UPPER'] = []
        result['B03_UPPER'] = []
        result['B04_UPPER'] = []
        result['B08_UPPER'] = []
        result['NDVI_UPPER'] = []
        result['SAVI_UPPER'] = []
        result['ENDVI_UPPER'] = []
        result['GNDVI_UPPER'] = []

        result['B02_LOWER'] = []
        result['B03_LOWER'] = []
        result['B04_LOWER'] = []
        result['B08_LOWER'] = []
        result['NDVI_LOWER'] = []
        result['SAVI_LOWER'] = []
        result['ENDVI_LOWER'] = []
        result['GNDVI_LOWER'] = []
        for date in dates:
            
            # BAND
            red = get_wavelength(X,Y,RED,date)
            blue = get_wavelength(X,Y,BLUE,date)
            green = get_wavelength(X,Y,GREEN,date)
            nir = get_wavelength(X,Y,NIR,date)

            # VI 
            ndvi = calculate_NDVI(nir,red)
            endvi = calculate_ENDVI(nir, green, blue)
            gndvi = calculcate_GNDVI(nir, green)
            savi = calculate_SAVI(nir, red, 0.5)

            # MASK + IMG
            img = get_image(X,Y,date)
            mask = get_mask_partition(X,Y,str(j))

            # MASKING + FILTER
            mask1 = mask[:,:,3] != 255
            mask2  =  np.logical_or(np.logical_or(img[:,:,0] >=200, img[:,:,1] >=200), img[:,:,2] >=200)
            mask3 = np.logical_or(mask1,mask2)
            
            # CALCULATE AVERAGE, STD

            red_res = ma.masked_array(red, mask=mask3)
            r_avg = red_res.mean()
            r_std = red_res.std()

            green_res = ma.masked_array(green, mask=mask3)
            g_avg = green_res.mean()
            g_std = green_res.std()

            blue_res = ma.masked_array(blue, mask=mask3)
            b_avg = blue_res.mean()
            b_std = blue_res.std()

            nir_res = ma.masked_array(nir, mask=mask3)
            n_avg = nir_res.mean()
            n_std = nir_res.std()

            if (r_avg is ma.masked or g_avg is ma.masked or b_avg is ma.masked or n_avg is ma.masked):
                continue
            if (r_std is ma.masked or g_std is ma.masked or b_std is ma.masked or n_std is ma.masked):
                continue

            ndvi_res = ma.masked_array(ndvi, mask=mask3)
            ndvi_avg = ndvi_res.mean()
            ndvi_std = ndvi_res.std()

            endvi_res = ma.masked_array(endvi, mask=mask3)
            endvi_avg = endvi_res.mean()
            endvi_std = endvi_res.std()

            gndvi_res = ma.masked_array(gndvi, mask=mask3)
            gndvi_avg = gndvi_res.mean()
            gndvi_std = gndvi_res.std()

            savi_res = ma.masked_array(savi, mask=mask3)
            savi_avg = savi_res.mean()
            savi_std = savi_res.std()

            # append result
            
            if (ndvi_avg is ma.masked or endvi_avg is ma.masked or gndvi_avg is ma.masked or savi_avg is ma.masked):
                continue
            if (ndvi_std is ma.masked or endvi_std is ma.masked or gndvi_std is ma.masked or savi_std is ma.masked):
                continue

            result[BLUE].append(b_avg)
            result['B02_LOWER'].append(b_avg-b_std)
            result['B02_UPPER'].append(b_avg+b_std)

            result[GREEN].append(g_avg)
            result['B03_LOWER'].append(g_avg-g_std)
            result['B03_UPPER'].append(g_avg+g_std)

            result[RED].append(r_avg)
            result['B04_LOWER'].append(r_avg-r_std)
            result['B04_UPPER'].append(r_avg+r_std)

            result[NIR].append(n_avg)
            result['B08_LOWER'].append(n_avg-n_std)
            result['B08_UPPER'].append(n_avg+n_std)

            result['NDVI'].append(ndvi_avg)
            result['NDVI_LOWER'].append(ndvi_avg-ndvi_std)
            result['NDVI_UPPER'].append(ndvi_avg+ndvi_std)

            result['ENDVI'].append(endvi_avg)
            result['ENDVI_LOWER'].append(endvi_avg-endvi_std)
            result['ENDVI_UPPER'].append(endvi_avg+endvi_std)

            result['GNDVI'].append(gndvi_avg)
            result['GNDVI_LOWER'].append(gndvi_avg-gndvi_std)
            result['GNDVI_UPPER'].append(gndvi_avg+gndvi_std)

            result['SAVI'].append(savi_avg)
            result['SAVI_LOWER'].append(savi_avg-savi_std)
            result['SAVI_UPPER'].append(savi_avg+savi_std)
            result['date'].append(date)

        df = pd.DataFrame(result)
        print(j)
        save_path = f'{path}result-{X}x-{Y}y-{j}'
        df.to_feather(save_path)      








X = '7680'
Y = '10240'

# generate_VI_timeseries_DF(X,Y, 'temp/')

# temp = pd.read_feather('temp/result-7680x-10240y-1')
# print(temp.head(10)) 

# temp2 = pd.read_feather('temp/result-7680x-10240y-2')
# print(temp2.head(10)) 

# temp2 = pd.read_feather('temp/result-7680x-10240y-3')
# print(temp2.head(10)) 
# df = pd.DataFrame({'x':[1]})
# j=1
# path = 'result/'
# save_path = f'{path}result-{X}x-{Y}y-{j}'
# df.to_feather(save_path)
# date = get_dates()[0]

# red = get_wavelength(X,Y,RED,date)
# img = get_image(X,Y,date)

# # # print(red)

# mx = ma.masked_array(np.array([1,2,3]), mask=[0, 0, 1])
# print(mx)
# print(type(mx[2]))
# print(mx[2]=='--')
# print(ma.masked)
# if(mx[2] is ma.masked ):
#     print('asd')
# else:
#     print('xxxx')

# mask = get_mask(X, Y)


# mask1 = mask[:,:,3] != 255


# # temp2 = img[:,:] >= [200,200,200]
# # print(temp)

# mask2  =  np.logical_or(np.logical_or(img[:,:,0] >=200, img[:,:,1] >=200), img[:,:,2] >=200)

# mask = np.logical_or(mask1,mask2)

# mx = ma.masked_array(red, mask=mask)
# print(mx.mean())
# print(mx.std())


# # print(temp)

# mx = ma.masked_array(red, mask=temp)
# print(mx)


# img = get_image(X,Y,'TCI',date)

# (img[:,:,0] > 200 
# print(temp)
#get_VI_DF('7680', '10240','data/')