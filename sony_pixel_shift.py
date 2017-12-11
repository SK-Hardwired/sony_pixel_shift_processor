#  State of art Sony pixel shift multi-frame processor
#  SK-Hardwired

# import the necessary packages
#from imutils import paths
#import argparse
import cv2
import numpy as np
import rawpy
import math
import Tkinter as tk
import tkFileDialog

# Function gamma correction
def gc(img, correction):
    img = img/(2.0**16-1)
    img = np.power(img, 1/correction)
    return np.uint16(img*(2.0**16-1))

# Function for making exposure and apply white balance
def scale(bayr,wbs):
    black = bl[0]#proc.imgdata.color.black
    if auto_bright == 1:
        saturation = 16320
    #else:
        #saturation = 16320
    #    saturation = np.max(bayr)

    #print (saturation)
    bayr = np.clip(bayr,black,uint14_max)                    # black subtraction
    bayr -= black
    bayr = np.float32(bayr)
    bayr *= (np.float16(uint14_max/(saturation - black)))
#    if auto_bright == 1:
#        bayr *= 65535/(2**16-1)
    bayr = np.clip(np.float32(bayr),0,uint14_max)  # clip to range
    bayr = np.float32(bayr)
    print 'Applying white balance coefficients to bayer image'
    bayr*=np.float32(wbs) #apply wb coeff red
    bayr=np.clip(bayr,0,2**14-1)
    return np.float32(bayr) 

# Function for saturation adjustment
def sat(bayr,K,sat_bit):
    for i in range (0,bayr.shape[1]) :
        bayr[:,i,0] = np.clip((bayr[:,i,0]*(0.114 + 0.886*K)+bayr[:,i,1]*(0.587 * (1-K))+bayr[:,i,2]*(0.299 * (1-K))),0,2**sat_bit-1)
        bayr[:,i,1] = np.clip((bayr[:,i,1]*(0.587 + 0.413*K)+bayr[:,i,2]*(0.299 * (1-K))+bayr[:,i,0]*(0.114 * (1-K))),0,2**sat_bit-1)
        bayr[:,i,2] = np.clip((bayr[:,i,2]*(0.299 + 0.701*K)+bayr[:,i,1]*(0.587 * (1-K))+bayr[:,i,0]*(0.114 * (1-K))),0,2**sat_bit-1)
#        bayr=np.clip(bayr,0,2**14-1)
    return np.float32(bayr)

root = tk.Tk()
root.withdraw()
F = []
#F.append(tkFileDialog.askopenfilename(filetypes=[('RAW from Sony Camera', ('*.arw','*.cr2'))]))

# List of files for processing (4 RAW files in Pixel-Shift series)
F.append('px_shft\\7R300061.ARW')
F.append('px_shft\\7R300062.ARW')
F.append('px_shft\\7R300063.ARW')
F.append('px_shft\\7R300064.ARW')
print F
bayr = []
cm = []
# Getting Bayer images from all 4 images
for f in F :
    f.encode('cp1251')
    print 'Opening files ',f
    with rawpy.imread(f) as raw:
            print 'Decoding bayer image from RAW'
            bayr.append(raw.raw_image_visible.copy())
            print 'Done'
            cm.append(raw.raw_colors_visible)
            cd = raw.color_desc
            print 'Color description', cd
            wb = np.float16(raw.camera_whitebalance)
            print 'RAW camera white balance coefficients = ',wb
            dwb = np.float16(raw.daylight_whitebalance)
            print 'RAW camera daylight WB preset coefficients = ',dwb
            bl = raw.black_level_per_channel
            print 'Black Level per channel from camera = ', bl

print 'RAW camera white balance coefficients = ',wb
print 'RAW camera daylight WB preset coefficients = ',dwb
print 'Black Level per channel from camera = ', bl

wb=wb/1000
r=[]
g1=[]
b=[]
g2=[]
auto_bright = 1
uint14_max = 2**14 - 1

# Aligning 1-pixel sensor offsets of images and bayer RGB colors to picture 1
bayr[1]=np.roll(bayr[1],1,axis=0)
cm[1]=np.roll(cm[1],-1,axis=0)

bayr[2]=np.roll(bayr[2],(1,-1),axis=(0,1))
cm[2]=np.roll(cm[2],(-1,1),axis=(0,1))

bayr[3] = np.roll(bayr[3],-1,axis=1)
cm[3]=np.roll(cm[3],1,axis=1)

# Getting color pixels from all 4 images to RGB channels
for i in range (0,4):
    r.append(bayr[i]*(cm[i] == 0).astype(int))
    g1.append(bayr[i]*(cm[i] == 1).astype(int))
    b.append(bayr[i]*(cm[i] == 2).astype(int))
    g2.append(bayr[i]*(cm[i] == 3).astype(int))

# Clearing temporary bayer images and color maps
bayr=None
cm=None

# Combining pixels to color channels
r = r[0]+(r[1])+r[2]+r[3]
print "Red assemble"
print r
g1=g1[0]+g1[1]+g1[2]+g1[3]
g2=g2[0]+g2[1]+g2[2]+g2[3]
print 'G1 assemble'
print g1
print 'G2 assemble'
print g2
g= np.median([g1,g2],axis=0)
print "G assemble"
print g
b =b[0]+b[1]+b[2]+b[3]
print "B assemble"
print b

r=np.float32(r)
g=np.float32(g)
b=np.float32(b)

r=scale(r,wb[0])
g=scale(g,wb[1])
b=scale(b,wb[2])

r=np.clip(r,0,65535)
g=np.clip(g,0,65535)
b=np.clip(b,0,65535)

r=np.float32(r)
g=np.float32(g)
b=np.float32(b)

r=np.clip(r,0,65535)
g=np.clip(g,0,65535)
b=np.clip(b,0,65535)

print 'Color channels minimums'
print 'Red = ',np.min(r)
print 'Green = ',np.min(g)
print 'Blue = ',np.min(b)

print 'Color channels maximums'
print 'Red = ',np.max(r)
print 'Green = ',np.max(g)
print 'Blue = ',np.max(b)

# Merging color channels to one picture
img = cv2.merge((b,g,r))

# Clearing temp color channels
r=None
g=None
b=None

img = np.float32(img)

# Applying gamma correction
img = gc(img,1.8)

###Sharpening (USM)###
gaussian_3 = cv2.GaussianBlur(img, (3,3), 3)
img = cv2.addWeighted(img, 3, gaussian_3, -2, 3)

print 'Img max,min after USM = ', np.max(img), np.min(img)

img+=np.amin(img)

# Saturation adjustment
img = sat(img,1.75,16)

# Stretching brightness to cover 16 bit per channel range
img*=4
img =np.clip(img,0,2**16-1)
img = np.uint16(img)
print 'Minimums'
print np.min(img)

print 'Maximums'
print np.max(img)

# Picking the ROI
img_view = img[1000:3000,1500:3500]

# Display processed image ROI
cv2.imshow('Pixel_shift image',img_view)

#Write image to 16-bit TIFF file
cv2.imwrite('bayr.tiff',img)

key = cv2.waitKey(0)
cv2.destroyAllWindows()
