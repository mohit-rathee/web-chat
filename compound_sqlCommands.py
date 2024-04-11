from sqlalchemy import create_engine, MetaData, Column, Integer, String, text , ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker , registry, declarative_base
from sqlalchemy.ext.automap import automap_base
import time, random

#new_table_name=str(random.randint(1,10000000))

Base = declarative_base()

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
class Users(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True)
    name=Column(String)


Base.metadata.create_all(bind=engine)

# Fetching the metadata from database to ORM.
Base.metadata.reflect(bind=engine)

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

new_table_name = '07032004'
# create a compound_sql command.
compound_sql = """
               BEGIN TRANSACTION;
               INSERT INTO users (name) VALUES ('Mohit User');
               CREATE TABLE '07032004' (
                id SERIAL PRIMARY KEY,
                data VARCHAR NOT NULL,
                sender_id INTEGER REFERENCES users(id)
               );

               COMMIT; """

start=time.time()

#execute our compound_sql
result = my_conn.executescript(compound_sql)
my_conn.commit()

#final = time.time()
#print("compound_sql execution : "+str((final-start)*1000))
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
#start=time.time()

# Manually create the class.
# Add it will automatically update the metadata.

attrs = {
    '__tablename__': str(new_table_name),
    'id': Column(Integer, primary_key=True),
    'data': Column(String, nullable=False),
    'sender_id': Column(Integer, ForeignKey(Users.id)),
}
# store this class into a variable or a dictionary.

# Linear Approach:
#channel_class = type(new_table_name, (Base,), attrs
#Base.metadata.create_all(bind=engine) # create the table by just one call
#Base.prepare(engine)
#final = time.time()
#print((final-start)*1000)
#print('--------')

# Constant Approach:
type(new_table_name, (Base,), attrs)
class channel_class(object):
    pass

# Instead of creating the tables just map the classes
#metadata.tables[new_table_name].metadata.create_all(engine)

mapper.map_imperatively(channel_class, metadata.tables[new_table_name],properties={
    'user': relationship(Users)
})

final = time.time()
print("update class execution time : "+str((final-start)*1000))
#print((final-start)*1000)
print('----------')

# checking the health of class

Session = sessionmaker(bind=engine)
session = Session()

user = Users(name="mohit")
session.add(user)
session.commit()

start=time.time()
test = channel_class(id=1,data="hello world!",sender_id=user.id)
session.add(test)
session.commit()
final = time.time()
print("Insert query time : "+str((final-start)*1000))

start = time.time()

data = session.query(channel_class).first()
print(data.data)
print(data.user.name)
print(data.sender_id)

final = time.time()
print("Read query time : "+str((final-start)*1000))

print('----------')

start = time.time()
sql_query = text("INSERT INTO users (name) VALUES ('heeeeeeeeha');")
session.execute(sql_query)
session.commit()
final = time.time()
print("Insert query time with sqlscript : "+str((final-start)*1000))

start = time.time()
sql_query = text("SELECT last_insert_rowid() AS id;")
result = session.execute(sql_query).fetchone()
session.commit()
final = time.time()
print("Read query time with sqlscript : "+str((final-start)*1000))
print("id is "+str(result[0]))
print('--------------------------')

connection.close()
