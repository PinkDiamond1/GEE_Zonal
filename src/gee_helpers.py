import ee, os, re
import pandas as pd
import geopandas as gpd
import geojson
from datetime import datetime
from shapely.geometry import Polygon, MultiPolygon
try:
    from pydrive.drive import GoogleDrive
    from pydrive.auth import GoogleAuth
except:
    print("Google Drive tools are not available")

pd.set_option('display.max_colwidth', None)

def gpd_to_gee(inD, id_col):
    ''' Create a google earth engine feature collection from a geopandas object
    :param inD: geopandas dataframe to convert to EE collection (for use in zonal stats
    :type inD: gpd.GeoDataframe
    :param id_col: column name in inD used to ID the features
    :type id_col: string 
    :return ee.featurecollection.FeatureCollection: feature collection to be used in zonal stats
    '''
    all_polys = []
    bad_idx = []
    for idx, row in inD.iterrows():
        try:
            shpJSON = geojson.Feature(geometry=row['geometry'], properties={"id":row[id_col]})
            if type(row['geometry']) == Polygon:
                ee_poly = ee.Geometry.Polygon(shpJSON['geometry']['coordinates'])
            elif type(row['geometry']) == MultiPolygon:
                ee_poly = ee.Geometry.MultiPolygon(shpJSON['geometry']['coordinates'])
            all_polys.append(ee_poly)
        except:
            print(idx)            
            bad_idx.append(idx)
    cur_ee = ee.featurecollection.FeatureCollection(all_polys)
    return(cur_ee)

def get_zonal_res(res):
    ''' create a data frame from the results of GEE zonal results (res.getInfo())
    '''
    all_res = []
    for feat in res['features']:
        all_res.append(feat['properties'])
    return(pd.DataFrame(all_res))

def authenticateGoogleDrive():
    gauth = GoogleAuth()
    drive = GoogleDrive(gauth)
    return drive