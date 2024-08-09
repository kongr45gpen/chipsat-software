# This code sourced from:
# DiffuserCam: Lensless Single-exposure 3D Imaging
# Nick Antipa*, Grace Kuo*, Reinhard Heckel, Ben Mildenhall, Emrah Bostan, Ren Ng, and Laura Waller
#
# https://github.com/Waller-Lab/DiffuserCam-Tutorial/blob/master/tutorial/GD.ipynb
#
# Licensed under BSD 3-Clause License
# Copyright (c) 2018, Waller Lab
# All rights reserved.
#

from machine import Pin
import image
from ulab import numpy as np
import time
import machine
import gc
import math
from machine import UART
import micropython
import pyb

#cam = Pin('D12', Pin.OUT)
#cam.off()

print("Camera pin set")

#psfs = image.Image("3_psfs.bmp", False)

#psfs.to_jpeg(x_scale=0.2, y_scale=0.2, encode_for_ide = True)
#print("Successfully encoded image")
#print(psfs)
#print("Successfully printed image")

#time.sleep(1)

# Downsampling factor (used to shrink images)
f = 1/10

# Number of iterations
iters = 100

PADDED_BUFFER_0 = None
PADDED_BUFFER_1 = None
PADDED_BUFFER_2 = None
PADDED_BUFFER_3 = None
Hre = None
Him = None
v = None

def dbg_gc(text=None, wait=False):
    gc.collect()
    return
    if wait:
        time.sleep_ms(10)
    before = gc.mem_alloc()
    gc.collect()
    after = gc.mem_alloc()
    free = gc.mem_free()
    if text is not None:
        print("({})".format(text), end=' ')
    print("[Used: {}, After: {}".format(before, after), end='')
    if wait:
        time.sleep_ms(50)
    print(", Free: {}]".format(before, free))
    if wait:
        time.sleep_ms(10)

def display(array, text=None):
    return # There are some issues with images being converted when displayed (probably because of the added text?)
    array /= np.max(array) / 255 # Expose to the Right
    img = image.Image(array, copy_to_fb=True)
    if text:
        img.draw_string(5,10, text)
    time.sleep(0.1)
    #img.to_jpeg(encode_for_ide=True, copy_to_fb=True)
    img.flush()

def fft2(real, imag=None):
    h, w = real.shape
    #print(f"Width={w}, height={h}")

    if imag is not None and real.shape != imag.shape:
        raise Exception("Different real/imag sizes")
    if math.log2(h) != math.ceil(math.log2(h)) or math.log2(w) != math.ceil(math.log2(w)):
        raise Exception("Sorry, I can only work with powers of 2 in dimensions :(")

    if imag is None:
        imag = np.zeros((h,w))

    for i in range(0, h): # for each row
        real[i], imag[i] = np.fft.fft(real[i], imag[i])

    for j in range(0, w): # for each column
        real[:,j], imag[:,j] = np.fft.fft(real[:,j], imag[:,j])

    return real, imag

def ifft2(real, imag=None):
    h, w = real.shape
    #print(f"Width={w}, height={h}")

    if imag is not None and real.shape != imag.shape:
        raise Exception("Different real/imag sizes")
    if math.log2(h) != math.ceil(math.log2(h)) or math.log2(w) != math.ceil(math.log2(w)):
        raise Exception("Sorry, I can only work with powers of 2 in dimensions :(")

    if imag is None:
        imag = np.zeros((h,w))

    for j in range(0, w): # for each column
        real[:,j], imag[:,j] = np.fft.ifft(real[:,j], imag[:,j])

    for i in range(0, h): # for each row
        real[i], imag[i] = np.fft.ifft(real[i], imag[i])

    return real, imag

def fftshift(arr):
    # Implementation from numpy
    for axis, dim in enumerate(arr.shape):
        shift = dim // 2
        gc.collect()
        arr = np.roll(arr, shift, axis=axis)

    return arr

def ifftshift(arr):
    # Implementation from numpy
    for axis, dim in enumerate(arr.shape):
        shift = -(dim // 2)
        gc.collect()
        arr = np.roll(arr, shift, axis=axis)

    return arr

def nextPow2(n):
    return int(2**np.ceil(np.log2(n)))

def calcA(vk):
    Vk_re, Vk_im = fft2(ifftshift(vk))
    vk = None
    dbg_gc()

    H_times_vk_re = Hre * Vk_re - Him * Vk_im
    H_times_vk_im = Hre * Vk_im + Him * Vk_re

    Are, Aim = ifft2(H_times_vk_re, H_times_vk_im)

    H_times_vk_re = None
    H_times_vk_im = None

    return crop(fftshift(Are)), crop(fftshift(Aim))

def calcAHerm(diff_re, diff_im):
    PADDED_BUFFER_0 = pad(diff_re) # xpad_re
    PADDED_BUFFER_1 = pad(diff_im) # xpad_im

    Xre, Xim = fft2(ifftshift(PADDED_BUFFER_0), ifftshift(PADDED_BUFFER_1))

    del diff_re, diff_im
    PADDED_BUFFER_0 = None
    PADDED_BUFFER_1 = None
    gc.collect()

    # We convert to adjoint here to save the space of storing Hadj as a
    # separate variable
    Hadj_times_X_re =   Xre * Hre + Xim * Him
    #Hadj_times_X_im = - Xre * Him + Xim * Hre
    PADDED_BUFFER_0 = - Xre * Him
    PADDED_BUFFER_1 =   Xim * Hre
    Xre = Xim = None
    Hadj_times_X_im = PADDED_BUFFER_0 + PADDED_BUFFER_1

    Aherm_re, Aherm_im = ifft2(Hadj_times_X_re, Hadj_times_X_im)
    del Hadj_times_X_re, Hadj_times_X_im
    gc.collect()

    PADDED_BUFFER_0 = fftshift(Aherm_re)
    PADDED_BUFFER_1 = fftshift(Aherm_im)

    Aherm_re = Aherm_im = None

    return PADDED_BUFFER_0, PADDED_BUFFER_1

def grad(vk):
    Av_re, Av_im = calcA(vk)
    diff_re = Av_re - data
    # diff_im = Av_im (no need for extra allocation)

    del vk, Av_re

    Aherm_re, _ = calcAHerm(diff_re, Av_im)

    del diff_re, Av_im

    return Aherm_re

def fista_update(vk, tk, xk):
    x_k1 = xk
    gradient = grad(vk)
    vk -= alpha*gradient
    xk = proj(vk)
    t_k1 = (1+np.sqrt(1+4*tk**2))/2
    vk = xk+(tk-1)/t_k1*(xk - x_k1)
    tk = t_k1

    return vk, tk, xk

def loaddata(show_im=True):
    global Hre, Him, v
    global psf, data #TODO remove
    # psf = Image.open(psfname).convert('L')
    # psf = np.array(psf, dtype='float32')
    # data = Image.open(imgname).convert('L')
    # data = np.array(data, dtype='float32')

    psf = image.Image("3_psfs.bmp")

    # Scaling with BICUBIC may be slower but it might do better against aliasing.
    # We don't use a more explicit demosaicing algorithm as in the original DiffuserCam.
    # I'm not sure how much worse this is.
    psf.to_grayscale(x_scale=f, y_scale=f, hint=image.BICUBIC)
    psf = psf.to_ndarray("f")
    # Python may not automatically remove the old image (before conversion to array),
    # so we explicitly clear some memory here
    gc.collect()

    data = image.Image("3_psfs_elsewhere.bmp")
    # Final data stored in the specialised frame buffer, which should be much larger
    # than the heap. Elsewhere we would run out of space here.
    data = data.to_grayscale(x_scale=f, y_scale=f, hint=image.BICUBIC, copy_to_fb=True)
    gc.collect()
    data = data.to_ndarray("f")
    gc.collect()
    
    print('Used: ' + str(gc.mem_alloc()) + ' Free: ' + str(gc.mem_free()))

    """In the picamera, there is a non-trivial background
    (even in the dark) that must be subtracted"""
    #bg = np.mean(psf[5:15,5:15])
    bg = 7.18 # We resized the image so original data is hard to get, use dummy value
    psf -= bg
    data -= bg

    psf /= np.linalg.norm(psf)
    data /= np.linalg.norm(data)

    #display(psf, "PSFS")
    #display(data, "Data")

    f_psf = open("f_psf.csv","w")
    for i in range(psf.shape[0]):
        for j in range(psf.shape[1]):
            f_psf.write(str(psf[i][j]) + ",")
        f_psf.write("\n")
    f_psf.close()

    f_data = open("f_data.csv", "w")
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            f_data.write(str(data[i][j]) + ",")
        f_data.write("\n")
    f_data.close()
    print("Successfully saved data to CSV")

    f_psf = None
    f_data = None

    # Initialise matrices
    pixel_start = (np.max(psf) + np.min(psf))/2
    init_shape = psf.shape

    print("Successfully loaded image {} x {}".format(init_shape[0], init_shape[1]))
    time.sleep(0.1)

    padded_shape = [nextPow2(2*n - 1) for n in init_shape]
    starti = (padded_shape[0]- init_shape[0])//2
    endi = starti + init_shape[0]
    startj = (padded_shape[1]//2) - (init_shape[1]//2)
    endj = startj + init_shape[1]
    hpad = np.zeros(padded_shape)
    hpad[starti:endi, startj:endj] = psf

    print("New padded size: {} x {}".format(padded_shape[0], padded_shape[1]))

    Hre, Him = fft2(ifftshift(hpad))
    # "Ortho" norm
    fct = 1 / np.sqrt(padded_shape[0] * padded_shape[1])
    Hre *= fct
    Him *= fct
    print("min Hre = {}, max Hre = {}, mean Hre = {}".format(np.min(Hre), np.max(Hre), np.mean(Hre)))
    print("min Him = {}, max Him = {}, mean Him = {}".format(np.min(Him), np.max(Him), np.mean(Him)))

    display(psf)
    #Hadj = np.conj(H)

    # We have allocated Hre, Him and will not use psf any more in the code.
    # So we can clear it from memory
    #psf = None
    hpad = None
    dbg_gc()

    v = np.zeros(padded_shape)
    v[starti:endi, startj:endj] = pixel_start

    return starti, endi, startj, endj, padded_shape

starti, endi, startj, endj, padded_shape = loaddata()

def crop(X):
    return X[starti:endi, startj:endj]

def pad(v):
    vpad = np.zeros(padded_shape)
    vpad[starti:endi, startj:endj] = v
    return vpad

# Preallocate memorys
dbg_gc()
PADDED_IMAGE_0 = np.zeros(Hre.shape)
PADDED_IMAGE_1 = np.zeros(Hre.shape)
PADDED_IMAGE_2 = np.zeros(Hre.shape)
PADDED_IMAGE_3 = np.zeros(Hre.shape)

print("Memory allocated")
time.sleep(0.1)

# Gradient descent
#crop = utils[0]
#pad = utils[1]
#utils = None

PADDED_IMAGE_0 = None
PADDED_IMAGE_1 = None
PADDED_IMAGE_2 = None
PADDED_IMAGE_3 = None
dbg_gc()
PADDED_IMAGE_0 = Hre**2
PADDED_IMAGE_1 = Him**2
PADDED_IMAGE_2 = PADDED_IMAGE_0 + PADDED_IMAGE_1

alpha = 1.8 / (np.max(PADDED_IMAGE_2))
print("max = {}, alpha = {}".format(np.max(PADDED_IMAGE_2), alpha))
iterations = 0

#PADDED_IMAGE_0 = None
#PADDED_IMAGE_1 = None
PADDED_IMAGE_2 = None
dbg_gc()

def non_neg(xi):
    xi = np.maximum(xi,0)
    return xi
#proj = lambda x:x #Do no projection
proj = non_neg #Enforce nonnegativity at every gradient step. Comment out as needed.

vk = v
tk = 1
xk = v

# Allocate a big contiguous area before iteration
PADDED = np.zeros(8000)

for iterations in range(iters):
    PADDED_IMAGE_0 = None
    PADDED_IMAGE_1 = None
    PADDED = None
    gc.collect()
    try:
        vk, tk, xk = fista_update(vk, tk, xk)
    except MemoryError as e:
        print(e)
        # Actually, ignoring the error might be a good solution?
    print(f"Iteration {iterations}")

    PADDED = np.zeros(8000)

result = proj(crop(vk))

result *= 255 / np.max(result)

image.Image(result).save("diffusercam_result.bmp")

gc.collect()
#initMatrices(psf)
print("Successfully init matrices")
print("                         ")

time.sleep(0.5)
