"""
basic stuff with arcpy geometry
"""
import arceditor
import arcpy
import os


def meters_to_feet(meters):
    feet = meters * 3.28084
    return feet


if __name__ == '__main__':
    sde_path = r'C:\users\jen\data\database.sde'
    spc = os.path.join(sde_path, 'my_table')

    cursor = arcpy.da.SearchCursor(spc, ['OID@', 'SHAPE@'])
    sr = arcpy.SpatialReference(4326)

    for row in cursor:
        oid = row[0]
        geom = row[1]
        if geom.isMultipart:
            for line in geom:
                newLine = arcpy.Polyline(line, sr)
                length = meters_to_feet(newLine.getLength())
                if length > 25000:
                    print('OID {} is a multi part feature that has at least one part > 25000 feet'.format(oid))
        else:
            length = meters_to_feet(geom.getLength())
            if length > 25000:
                print('OID {} is a single part feature that is > 25000 feet'.format(oid))
