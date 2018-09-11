"""Reprojecting with the gdal/ogr python bindings"""
import csv

import ogr, osr


def reproject_point(inputEPSG, outputEPSG, pointX, pointY):

    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(pointX, pointY)

    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(inputEPSG)

    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(outputEPSG)

    coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

    point.Transform(coordTransform)
    return point.GetX(), point.GetY()


if __name__ == '__main__':
    with open(r'bboxes.csv') as csvIn:
        reader = csv.reader(csvIn, delimiter=',', quotechar='"')
        with open('bboxes32614.csv', 'wb') as csvOut:
            writer = csv.writer(csvOut)
            for row in reader:
                minY = float(row[0])
                minX = float(row[1])
                maxY = float(row[2])
                maxX = float(row[3])
                width = int(row[4])
                height = int(row[5])

                newMinX, newMinY = reproject_point(4326, 32614, minX, minY)
                newMaxX, newMaxY = reproject_point(4326, 32614, maxX, maxY)
                writer.writerow([newMinY, newMinX, newMaxY, newMaxX, width, height])
