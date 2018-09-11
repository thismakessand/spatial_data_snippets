#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random

import pandas as pd
import pyodbc
import geopandas as gpd
from shapely.wkt import loads


def get_some_polygons():
    """Get some sample polygons

    :rtype: geopandas.GeoDataFrame
    """
    conn = pyodbc.connect(conn_str)
    select_stmt = """SELECT PolygonName, geometry.STAsText() as WKT FROM sample_polygons"""
    df = pd.read_sql(select_stmt, conn)
    gdf = gpd.GeoDataFrame(df, crs={'init': 'epsg:4326'}, geometry=df['WKT'].map(loads))
    gdf.drop('WKT', axis=1, inplace=True)
    return gdf


def get_some_points():
    """Get some sample points

    :rtype: geopandas.GeoDataFrame
    """
    point_geoms = pd.Series(["POINT ({x} {y})".format(
        x=round(random.uniform(-130,-100), 5),
        y=round(random.uniform(30,50), 5))
        for i in range(0, 10000)])
    gdf = gpd.GeoDataFrame(point_geoms,
                           crs={'init': 'epsg:4326'},
                           geometry=point_geoms.map(loads))
    return gdf


if __name__ == '__main__':
    conn_str = ""

    polys = get_some_polygons()
    points = get_some_points()

    # Spatial join point to polys

    joined = gpd.sjoin(points,
                       polys,
                       how='inner',
                       op='intersects')

    if not joined.empty:
        points["Polygon"] = joined.groupby(level=0)["PolygonName"].transform(lambda x: ','.join(x))
