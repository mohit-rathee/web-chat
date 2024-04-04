from os import walk
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, text
from sqlalchemy.orm import sessionmaker , registry
from sqlalchemy.ext.automap import automap_base
import time, random

new_table_name=str(random.randint(1,1000))

Base = automap_base()

#db_uri = 'sqlite:///testBydevelop.sqlite3'
db_uri = 'sqlite:///testBydevelop.sqlite3'

# Create an SQLAlchemy engine object
# which will store the connection.
engine = create_engine(db_uri)


# create a connection
connection = engine.connect()
my_conn = connection.connection

# Create a metadata object
# which will store the metadata of db.
metadata = MetaData()

#manually creating a table.
Table('users', metadata,
              Column('id', Integer, primary_key=True),
              Column('name', String(50)))

metadata.create_all(bind=engine)

# Fetching the metadata from database to ORM.
metadata.reflect(bind=engine)

# creating classes from the metadata
# After this all the tables will be in Base.classes object
Base=automap_base(metadata=metadata)
Base.prepare(engine)


#====================TESTING___START=======================

# PREVIOUSLY

#start = time.time()
#
# Add table to local metadata.
#Table('test3', metadata,
#              Column('id', Integer, primary_key=True),
#              Column('name', String(50)))
#
# Then create that table
#metadata.create_all(bind=engine)
#
#final = time.time()
#print((final-start)*1000)
#
# Then create classes for the table.
#Base.prepare(engine)
#
#final = time.time()
#print((final-start)*1000)

# NEW_SOLUTION

# create a mapper for final solution
mapper = registry()

# create a compound_sql command.
compound_sql = """
               BEGIN TRANSACTION;
               INSERT INTO users (name) VALUES ('Mohit User');
               CREATE TABLE '"""+new_table_name+"""' ( id INTEGER PRIMARY KEY, name varchar(50));
               COMMIT; """

start=time.time()

#execute our compound_sql
result = my_conn.executescript(compound_sql)
my_conn.commit()

final = time.time()
print("compound_sql execution : "+str((final-start)*1000))
#print((final-start)*1000)

# un-successfull event : TOOK (~35 to ~45 ms)
    #to get new table into metadata, we have 2 options.
        #metadata.reflect(bind=engine)
        #----OR----
        #Table('test', metadata,
        #              Column('id', Integer, primary_key=True),
        #              Column('name', String(50)))
    #to get the class.
        #Base.prepare(engine)

# successfull event:
start=time.time()

# Manually create the class.
# Add it will automatically update the metadata.

attrs = {
    '__tablename__': new_table_name,
    'id': Column(Integer, primary_key=True),
    'name': Column(String(50)),
}
# store this class into a variable or a dictionary.

# Linear Approach:
#channel_class = type(new_table_name, (Base,), attrs)
#Base.metadata.create_all(bind=engine) # create the table by just one call
#Base.prepare(engine)
#final = time.time()
#print((final-start)*1000)
#print('--------')

# Constant Approach:
type(new_table_name, (Base,), attrs)
class channel_class(object):
    pass
metadata.tables[new_table_name].metadata.create_all(engine)
mapper.map_imperatively(channel_class, metadata.tables[new_table_name])
final = time.time()
print("update class execution time : "+str((final-start)*1000))
#print((final-start)*1000)
print('--------')

# checking the health of class

start=time.time()
Session = sessionmaker(bind=engine)
session = Session()
test = channel_class(id=1,name="mohit")
session.add(test)
session.commit()
final = time.time()
print("Insert query time : "+str((final-start)*1000))

start = time.time()
result = session.query(channel_class).all()
final = time.time()
print("read query time : "+str((final-start)*1000))

connection.close()
