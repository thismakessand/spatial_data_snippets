"""Read WKT geoms from text file; reproject with pyproj; write to shapefile"""
import json

from fiona import collection
from fiona.crs import from_epsg
import pyproj
import shapely.wkt
import shapely.geometry
from shapely.ops import transform
import toolz


f = '/home/jen/Downloads/geoms.txt'

src_prj = pyproj.Proj(init='epsg:3857')
dst_prj = pyproj.Proj(init='epsg:4326')
project = toolz.curry(pyproj.transform)(src_prj, dst_prj)  # toolz' curry makes any function into a partial!

with open(f, 'r') as input:
    schema = {'geometry': 'Polygon', 'properties': {'id': 'str', 'state': 'str'}}
    with collection('bad_shapes.shp', 'w',
            crs=from_epsg(4326),
            driver="ESRI Shapefile",
            schema=schema
    ) as output:
        for row in input:
            id, state, wkt = row.split('\t')
            shp = shapely.wkt.loads(wkt)
            wgs84 = transform(project, shp)
            output.write({"properties": {"id": id, "state": state},
                         "geometry": shapely.geometry.mapping(wgs84)})
