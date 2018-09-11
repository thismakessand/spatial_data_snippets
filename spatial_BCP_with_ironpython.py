"""
Sample using SQL Server BCP with IronPython (let's hope it doesn't come to this)
"""
import clr
import datetime
import json
import math
import random

clr.AddReference('System')
clr.AddReference('System.Data')
from System import Array, Int32, Double, String, Environment
from System.Data import SqlClient, DataTable


def fetch_sample_data():
    return [{"id": i,
             "geometry": "POINT ({x} {y})".format(
                 x=round(random.uniform(-180,180), 5),
                 y=round(random.uniform(-90,90), 5))}
            for i in range(0, 10000)]


if __name__ == '__main__':
    connection_params = {
        "user": "admin",
        "password": "*****",
        "instance": "localhost\\SQLEXPRESS"
    }
    tableName = 'test'

    sqlConnectionString = "Persist Security Info=False;User ID={user};Password={password};Initial Catalog=test;Server={instance}".format(**connection_params)

    data = fetch_sample_data()

    fields = [
        "id",
        "geometry"
    ]

    t0 = datetime.datetime.now()
    tbl = DataTable()

    for field in fields:
        if type(data[0][field]) is int:
            tbl.Columns.Add(field, Int32)
        elif type(data[0][field]) is float:
            tbl.Columns.Add(field, Double)
        else:
            tbl.Columns.Add(field, String)

    for row in data:
        newRow = [
            row[x] for x in fields
        ]
        tbl.Rows.Add(Array[object](newRow))

    t1 = datetime.datetime.now()
    print("Building DataTable object: {}".format(t1-t0))

    with SqlClient.SqlConnection(sqlConnectionString) as sqlDbConnection:
        sqlDbConnection.Open()

        cmd = SqlClient.SqlCommand("truncate table {}".format(tableName), sqlDbConnection)
        cmd.ExecuteNonQuery()
        t2 = datetime.datetime.now()
        print("Truncated table: {}".format(t2-t1))
        with SqlClient.SqlBulkCopy(sqlConnectionString,
                                   SqlClient.SqlBulkCopyOptions.TableLock,
                                   BulkCopyTimeout=0,
                                   DestinationTableName=tableName) as bcp:
            bcp.WriteToServer(tbl)
        t3 = datetime.datetime.now()
        print("Write rows: {}".format(t3-t2))
        print("Total: {}".format(t3-t0))

        sqlDbConnection.Close()

    Environment.Exit(0)
