"""
Messing around with SQL Server binary geometry data with SQL Alchemy
"""
import binascii

from sqlalchemy import Column, Integer, create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import expression
from sqlalchemy.types import UserDefinedType

from readers.db import windowed_query, column_windows


class GisElement(object):
    """from http://docs.sqlalchemy.org/en/latest/_modules/examples/postgis/postgis.html
    Represents a geometry value."""

    def __str__(self):
        return self.desc

    def __repr__(self):
        return "<%s at 0x%x; %r>" % (self.__class__.__name__,
                                    id(self), self.desc)


class BinaryGisElement(GisElement, expression.Function):
    """Represents a Geometry value expressed as binary.  Extended for SQL Server spatial types"""

    def __init__(self, data, srid):
        self.data = data
        expression.Function.__init__(self, "geometry::STGeomFromWKB", data, srid,
                                    type_=Geometry(coerce_="binary"))

    @property
    def desc(self):
        return self.as_hex

    @property
    def as_hex(self):
        return binascii.hexlify(self.data)


class TextualGisElement(GisElement, expression.Function):
    """Represents a Geometry value expressed as text.  Extended for SQL Server spatial types"""

    def __init__(self, desc, srid):
        self.desc = desc
        expression.Function.__init__(self, "geometry::STGeomFromText", desc, srid, type_=Geometry(coerce_="text"))


class Geometry(UserDefinedType):

    name = "GEOMETRY"
    # from_text = 'geometry::STGeomFromText'

    def __init__(self, dimension=None, srid=4326,
                 coerce_="text"):
        self.dimension = dimension
        self.srid = srid
        self.coerce = coerce_


    def _coerce_compared_value(self, op, value):
        return self

    def get_col_spec(self):
        return self.name

    # def column_expression(self, col):
    #     return func.STAsText(col, type_=self)


    def bind_expression(self, bindvalue):
        if self.coerce == "text":
            return TextualGisElement(bindvalue, self.srid)
        elif self.coerce == "binary":
            return BinaryGisElement(bindvalue, self.srid)
        else:
            assert False
    # def bind_expression(self, bindvalue):
    #     return TextualGisElement(bindvalue)  # THIS WORKS WITH SRID
        # return getattr(func, self.from_text)(bindvalue, type_=self)  # THIS WORKS for geometry:: part but does not work for SRID

    def column_expression(self, col):
        if self.coerce == "text":
            return getattr(func, "geometry::STAsText")(col, type_=self)
            # return func.STAsText(col, type_=self)
        elif self.coerce == "binary":
            return func.STAsBinary(col, type_=self)
        else:
            assert False

    def bind_processor(self, dialect):
        def process(value):
            if isinstance(value, GisElement):
                return value.desc
            else:
                return value

        return process

    def result_processor(self, dialect, coltype):
        if self.coerce == "text":
            fac = TextualGisElement
        elif self.coerce == "binary":
            fac = BinaryGisElement
        else:
            assert False

        def process(value):
            if value is not None:
                return fac(value)
            else:
                return value

        return process

    def adapt(self, impltype):
        return impltype(dimension=self.dimension,
                        srid=self.srid, coerce_=self.coerce)


class AugmentedBase:
    """To serialize sql alchemy row objects to python dictionaries
    """
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


if __name__ == '__main__':
    connection_params = {
        "host": "",
        "user": "",
        "password": "",
        "database": "",
        "schema": 'dbo',
    }
    connection_string = "mssql+pyodbc://{user}:{password}@{host}/{database}?driver=ODBC Driver 13 for SQL Server".format(
        **connection_params)

    engine = create_engine(connection_string, echo=False)

    Base = declarative_base(engine)

    table_atts = {
        '__tablename__': 'my_table_20160912',
        '__table_args__': {'autoload': False},
        'id': Column(Integer, primary_key=True),
        'GEOM': Column(Geometry)
    }

    # for this test case we don't have the table name upfront and __tablename__ can't be set after initialization,
    # so create the Base class dynamically:
    Sample = type('Sample', (Base, AugmentedBase), table_atts)

    s = Session(engine)
    q = s.query(Sample)

    # this operates on each whereclause generated from the windowing function:
    # the windowing function uses sql server row_number() to determine the pk id for each group - this is an example
    # # of the sql that is generated:
    # SELECT anon_1.id AS anon_1_id
    # FROM (SELECT my_table_20160912.id AS id, row_number() OVER (ORDER BY my_table_20160912.id) AS rownum
    # FROM my_table_20160912) AS anon_1
    # WHERE rownum % 100=1

    for whereclause in column_windows(q.session, Sample.id, 100):  # this returns a list of whereclauses which is essentially 'where id >= A and id < B'
        # eg, if you just want to execute each whereclause and deal with each chunk of rows individually:
        rows = q.filter(whereclause).order_by(Sample.id).all()
        bulk_obj = [row.as_dict() for row in rows]    # this converts the row objects that are returned into python dictionaries with 'column': 'value' pairs

        # TODO do something with the rows
        print(rows)

    # this operates on every row in the table
    for row in windowed_query(q, Sample.id, 100):
        print("data:", row.id)