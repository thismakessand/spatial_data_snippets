"""
Sql server spatial can't calculate the centroid of a multipoint geometry; use shapely for the calculation
"""
import json

import pyodbc
import shapely.wkb
import shapely.geometry


if __name__ == '__main__':
    connection_params = {
            "host": "",
            "username": "",
            "password": "",
            "database": ""
        }

    conn_str = (
        "DRIVER=ODBC Driver 13 for SQL Server;"
        "SERVER={host};"
        "DATABASE={database};"
        "UID={username};PWD={password};"
    ).format(**connection_params)

    select_stmt = """SELECT id, Geometry.STAsBinary() as geom from my_table WHERE Geometry is NOT NULL"""

    conn = pyodbc.connect(conn_str)
    cur = conn.cursor()
    rows = cur.execute(select_stmt).fetchall()

    centroids = []
    for row in rows:
        shp = shapely.wkb.loads(row.geom)
        geojson = json.dumps(shapely.geometry.mapping(shp))
        centroid = shp.centroid
        x, y = centroid.x, centroid.y
        centroids.append((row.id, geojson, x, y))

    create_table = """CREATE TABLE #tempCentroids (
        id INT NOT NULL,
        GeometryGeoJson varchar(MAX) NULL,
        CentroidLongitude Numeric(8,4) NULL,
        CentroidLatitude Numeric(8,4) NULL
      )
    """

    cur.execute(create_table)
    cur.commit()

    sql = """INSERT INTO #tempCentroids (id, GeometryGeoJson, CentroidLongitude, CentroidLatitude) VALUES (?,?,?,?)"""
    cur.executemany(sql, centroids)
    cur.commit()

    sql = """UPDATE r
        SET CentroidLongitude = c.CentroidLongitude,
        CentroidLatitude = c.CentroidLatitude,
        GeometryGeoJson = c.GeometryGeoJson
        FROM #tempCentroids c
        INNER JOIN my_table r
        ON r.id = c.id
        """
    cur.execute(sql)
    cur.commit()
    cur.close()
    conn.close()
