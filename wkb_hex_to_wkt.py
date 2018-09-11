"""messing around with wkb/wkt"""
import fiona
from fiona.crs import from_epsg
from shapely import wkb, wkt
from shapely.geometry import mapping


if __name__ == '__main__':

    geom_string = '0101000020110F00009548A88F1AD163C1061A928AEAEA4C41'

    wkb_bytes = bytes.fromhex(geom_string)

    shape = wkb.loads(wkb_bytes)

    # to wkt:
    print(wkt.dumps(shape))

    # POINT (-10389716.4892924223095179 3790293.0825836686417460)

    # OR, IN POSTGIS:  select ST_AsText('0101000020110F00009548A88F1AD163C1061A928AEAEA4C41'::geometry)

    # to shapefile:

    schema = {
        'geometry': "Point",
        "properties": {
            "ID": "str"
        }
    }

    with fiona.open('test.shp', 'w', driver='ESRI Shapefile', crs=from_epsg(3857), schema=schema) as dst:
        record = {
            "geometry": mapping(shape),
            "properties": {
                "ID": "1"
            }
        }
        dst.write(record)