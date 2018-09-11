# Sample script that uses arcpy da cursors to read from a flat (non-spatial) source table, create point geometries
# from lat/long fields and insert into a target feature class
import arceditor
import arcpy


if __name__ == '__main__':
    sourceTbl = '/path/to/your/source_table'
    targetFC = '/path/to/your/target_featureclass'

    sr = arcpy.SpatialReference(4267)   # NAD27

    sourceFields = [field.name for field in arcpy.ListFields(sourceTbl)]  # get list of fields in source table and add shape field
    sourceFields.extend(["SHAPE@XY"])

    targetCursor = arcpy.da.InsertCursor(targetFC, sourceFields)   # create insert cursor on target feature class

    yField = "latitude"
    xField = "longitude"
    xFieldIndex = [i for i, x in enumerate(sourceFields) if x == xField][0]   # get field position numbers for lat/long fields
    yFieldIndex = [i for i, x in enumerate(sourceFields) if x == yField][0]

    with arcpy.da.SearchCursor(sourceTbl, "*") as sourceCursor:
        for row in sourceCursor:
            Y = row[yFieldIndex]
            X = row[xFieldIndex]
            point = arcpy.Point(X, Y)
            pointGeom = arcpy.PointGeometry(point, sr)      # create point geometries and assign spatial reference
            row = row + (pointGeom,)
            targetCursor.insertRow(row)

    del targetCursor  # delete cursor to remove lock on target feature class