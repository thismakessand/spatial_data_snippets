#! /usr/bin/env python3.6
from collections import OrderedDict
from functools import partial

import dataset
import fiona
import pyproj
from shapely.geometry import shape
from shapely.ops import transform


if __name__ == '__main__':
    params = {
        "host": "",
        "user": "***",
        "password": "****",
        "database": "",
        "schema": "dbo",
        "table_name": "test",
    }

    connection_string = "mssql+pymssql://{user}:{password}@{host}/{database}".format(**params)

    db = dataset.connect(connection_string, schema=params['schema'], reflect_metadata=False)

    table = db.load_table(params['table_name'])
    table.delete()


    with fiona.drivers():
        with fiona.open(path='/home/jen/Downloads/shps/sample.shp', driver='ESRI Shapefile') as source:
            source_epsg = source.crs['init']
            project = partial(
                pyproj.transform,
                pyproj.Proj(init=source_epsg),  # source coordinate system
                pyproj.Proj(init='epsg:4326'))  # destination coordinate system
            def convert_geom(geom):
                projected_geom = transform(project, shape(geom))
                wkt = projected_geom.wkt
                return wkt


            rows = [(OrderedDict(dict(**row['properties'], GEOM=convert_geom(row['geometry'])))) for row in source]

            #for row in rows:
            #    table.insert(row)
            table.insert_many(rows=rows, chunk_size=1000, ensure=False)

            # Set SRID on geometries
            db.query("""UPDATE {table_name} SET GEOM.STSrid = 4326 WHERE GEOM IS NOT NULL;""".format(**params))
