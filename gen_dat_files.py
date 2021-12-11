"""
Generating the .dat files
"""
import sys
import os
import glob
import rs2
import numpy as np
from osgeo import gdal, gdalnumeric, ogr, osr


def save_vi_dat_files(out, vi_name, filename, x, y, transform, proj, raster, alpha = None):
    """    Saves the .dat files for the given Vegitation Index (VI)

           Args:
            out (str)           : The directory to which the results will be saved
            vi_name (str)       : Name of the VI for which the dat file will be created
            file_name (str)     : Name of the orthomosaic image file
            x (int)             : x size of the orthomosaic
            y (int)             : y size of the orthomosaic
            transform (tuple)   : Orthomosaic geotransform
            proj (tuple)        : Orthomosaic projection
            raster (numpy array): Raster that has the data to be stored
            alpha (numpy array) : Raster that has the data to be stored -only for RGB images- (defualt is None)

           Returns:
            none
    """
    dat_files_dir = os.path.join(out, vi_name) # create output folder for dat files
    if not os.path.exists(dat_files_dir):
        os.makedirs(dat_files_dir)

    out_file = os.path.join(dat_files_dir, filename + '_' + vi_name + '.dat')
    driver = gdal.GetDriverByName("ENVI")
    outds = driver.Create(out_file, x, y, 2, gdal.GDT_Float32)
    outds.SetGeoTransform(transform)
    outds.SetProjection(proj)
    outds.GetRasterBand(1).WriteArray(raster)
    if alpha is not None:
        outds.GetRasterBand(2).WriteArray(alpha)
    outds = None

def get_dat_for_vi(image_files, out_dir, img_type, vis_list):
    """    Generates the .dat files for the given Vegitation Indecies (VIs)

           Args:
            image_files (list(str)) : List of image filenames for all orthomosaic images to be processed
            out_dir (StringVar)     : The directory to which the results will be saved
            img_type (str)          : Type of images to be processed: RGB or MULTI
            vis_list (list(str))    : List of VIs to be generated for the orthomosaic(s)

           Returns:
            none
    """
    if img_type == 'RGB':
        for f in image_files:
            img_filename = os.path.splitext(os.path.basename(f))[0][:] # get filename without extension
            # Open image and get some of its parameters
            in_img = rs2.RSImage(f)
            x_size = in_img.ds.RasterXSize
            y_size = in_img.ds.RasterYSize
            geo_transform = in_img.ds.GetGeoTransform()
            geo_proj = in_img.ds.GetProjection()

            # Read bands
            red = in_img.img[0,:,:].astype(np.float32)
            green = in_img.img[1,:,:].astype(np.float32)
            blue = in_img.img[2,:,:].astype(np.float32)
            alpha = in_img.img[3,:,:].astype(np.float32)

            in_img = None

            for vi in vis_list:
                # process selected vi
                if vi == 'exg':
                    red_s = np.float32(red)/np.float32(red+green+blue) #TODO: check why float is needed again!
                    green_s = np.float32(green)/np.float32(red+green+blue)
                    blue_s = np.float32(blue)/np.float32(red+green+blue)
                    vi_raster = 2 * green_s - red_s - blue_s
                    save_vi_dat_files(out_dir, vi, img_filename[0:8], x_size, y_size, geo_transform, geo_proj, vi_raster, alpha)
                    vi_raster = None; red_s = None; green_s = None; blue_s = None
                if vi == 'grvi':
                    vi_raster = (green - red) / (green + red)
                    save_vi_dat_files(out_dir, vi, img_filename[0:8], x_size, y_size, geo_transform, geo_proj, vi_raster, alpha)
                    vi_raster = None
                if vi == 'mgrvi':
                    vi_raster = np.float32(green**2 - red**2) / np.float32(green**2+red**2)
                    save_vi_dat_files(out_dir, vi, img_filename[0:8], x_size, y_size, geo_transform, geo_proj, vi_raster, alpha)
                    vi_raster = None
                if vi == 'rgbvi':
                    vi_raster = (green**2 - red * blue) / (green**2 + red * blue)
                    save_vi_dat_files(out_dir, vi, img_filename[0:8], x_size, y_size, geo_transform, geo_proj, vi_raster, alpha)
                    vi_raster = None
                if vi == 'exgr':
                    red_s = np.float32(red)/np.float32(red+green+blue) #TODO: check why float is needed again!
                    green_s = np.float32(green)/np.float32(red+green+blue)
                    blue_s = np.float32(blue)/np.float32(red+green+blue)
                    vi_raster = 2 * green_s - red_s - blue_s - 1.4 * red_s - green_s
                    save_vi_dat_files(out_dir, vi, img_filename[0:8], x_size, y_size, geo_transform, geo_proj, vi_raster, alpha)
                    vi_raster = None
                if vi == 'cc':#
                    th1 = 0.95; th2 = 0.95; th3 = 20
                    i1 = red / green; i2 = blue / green; i3 = 2 * green - blue - red
                    cond1 = i1 < th1; cond2 = i2 < th2; cond3 = i3 > th3
                    i1 = None; i2 = None; i3 = None
                    vi_raster = (cond1 * cond2 * cond3)
                    cond1 = None; cond2 = None; cond3 = None
                    save_vi_dat_files(out_dir, vi, img_filename[0:8], x_size, y_size, geo_transform, geo_proj, vi_raster)
                    vi_raster = None

        red = None; green = None; blue = None; alpha = None

    if img_type == 'MULTI':
        for f in image_files:
            img_filename = os.path.splitext(os.path.basename(f))[0][:] # get filename without extension
            # Open image without loading to memory
            in_img = rs2.RSImage(f)
            blue = in_img.img[0,:,:].astype(np.float32)
            green = in_img.img[1,:,:].astype(np.float32)
            red = in_img.img[2,:,:].astype(np.float32)
            rededge = in_img.img[3,:,:].astype(np.float32)
            nir = in_img.img[4,:,:].astype(np.float32)

            in_img = None

            for vi in vis_list:
                if vi == 'ndvi':
                    vi_raster = (nir - red)/(nir + red)
                    save_vi_dat_files(out_dir, vi, img_filename[0:8], x_size, y_size, geo_transform, geo_proj, vi_raster)
                    vi_raster = None
                if vi == 'ndre':
                    vi_raster = (nir - rededge)/(nir + rededge)
                    save_vi_dat_files(out_dir, vi, img_filename[0:8], x_size, y_size, geo_transform, geo_proj, vi_raster)
                    vi_raster = None
                if vi == 'gndvi':
                    vi_raster = (nir - green)/(nir + green)
                    save_vi_dat_files(out_dir, vi, img_filename[0:8], x_size, y_size, geo_transform, geo_proj, vi_raster)
                    vi_raster = None
                if vi == 'savi':
                    vi_raster = ((nir - red)*(1.5))/(nir + red + 0.5)
                    save_vi_dat_files(out_dir, vi, img_filename[0:8], x_size, y_size, geo_transform, geo_proj, vi_raster)
                    vi_raster = None
                if vi == 'osavi':
                    vi_raster = ((nir - red)*(1.16))/(nir + red + 0.16)
                    save_vi_dat_files(out_dir, vi, img_filename[0:8], x_size, y_size, geo_transform, geo_proj, vi_raster)
                    vi_raster = None
                if vi == 'msavi':
                    vi_raster = 0.5*(2*nir+1-((2*nir+1)**2-8*(nir-red))**(1.0/2))
                    save_vi_dat_files(out_dir, vi, img_filename[0:8], x_size, y_size, geo_transform, geo_proj, vi_raster)
                    vi_raster = None
                if vi == 'gci':
                    vi_raster = gci = nir/green - 1
                    save_vi_dat_files(out_dir, vi, img_filename[0:8], x_size, y_size, geo_transform, geo_proj, vi_raster)
                    vi_raster = None
                if vi == 'reci':
                    vi_raster = nir/rededge - 1
                    save_vi_dat_files(out_dir, vi, img_filename[0:8], x_size, y_size, geo_transform, geo_proj, vi_raster)
                    vi_raster = None
                if vi == 'grvi':
                    vi_raster = (green - red)/(green + red)
                    save_vi_dat_files(out_dir, vi, img_filename[0:8], x_size, y_size, geo_transform, geo_proj, vi_raster)
                    vi_raster = None

            blue = None; green = None; red = None; rededge = None; nir = None
