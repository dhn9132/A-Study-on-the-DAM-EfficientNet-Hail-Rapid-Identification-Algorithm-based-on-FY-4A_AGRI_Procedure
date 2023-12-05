import os
import glob
from satpy.scene import Scene
import cartopy.feature as cfeature
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import geopandas as gpd

# Loading the FY4A files
filenames = glob.glob('./FY4A-_AGRI--_N_DISK_1047E_L1-_FDI-_MULT_NOM_20190304070000_20190304071459_4000M_V0001.HDF')

# Creating scene object
scn = Scene(filenames, reader='agri_fy4a_l1')

# Loading the true color composite
composite = 'true_color'
scn.load([composite])

# Set the Pytroll Projection Config Directory
os.environ['PPP_CONFIG_DIR'] = './'

# Resampling to the area of interest
china_area = scn.resample('china_area')

# Using Cartopy to add the boundary and province lines
fig = plt.figure(figsize=(12, 8))
ax = plt.axes(projection=ccrs.PlateCarree())

# Add the image to the plot
img = china_area.show(composite)
img.save('./true_color_image.png')
# china_boundary_shapefile = 'E:/china_basic_map_micaps4/bou2_4l.shp'
# china_provinces_shapefile = 'E:/china_basic_map_micaps4/bou2_4p.shp'