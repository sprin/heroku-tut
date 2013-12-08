"""
Import Table objects for use with Expression Language from this module.
"""
from sqlalchemy import create_engine, MetaData

from app import app
from sqlalchemy.pool import StaticPool

# Use a connection pool size of one.
engine = create_engine(
    app.config['DB_CONN_URI'],
    poolclass=StaticPool,
    isolation_level="AUTOCOMMIT",
)

meta = MetaData()
meta.bind = engine

## Reflect SQL views.
# This creates a persistent connection, which will be
# retained by the SQLAlchemy connection pool.

## Reflection
reflected = None
def reflect_database():
    """
    This can be called to update the reflected objects, so long as
    `reflected` is always prefixed by the module when referenced.
    """
    global reflected
    meta.tables = {}
    meta.reflect(views=True)
    reflected = meta.tables
    return reflected.keys()
reflect_database()

def result_as_list_of_dicts(query):
    """
    This function takes an SQL Alchemy Expression Language select object
    and executes it.
    It returns a dictionary, where the keys are the column names
    returned by the query.
    """
    # Get a connection and execute the query.
    conn = engine.connect()
    cur = conn.execute(query)

    desc = cur.keys()
    return [
        dict(zip([col for col in desc], row))
        for row in cur.fetchall()
    ]

