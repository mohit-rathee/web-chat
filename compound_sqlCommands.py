from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, text
from sqlalchemy.orm import sessionmaker
import time

# Replace 'your_database_uri' with the actual URI of your database
# Example: 'sqlite:///example.db' for SQLite
# For other databases, the URI format may differ
db_uri = 'sqlite:///testBydevelop.sqlite3'
#db_uri = 'sqlite:///testBydevelop2.sqlite3'

# Create an SQLAlchemy engine
engine = create_engine(db_uri)
Session = sessionmaker(bind=engine)
session=Session()
# Establish a connection
connection = engine.connect()
my_conn = connection.connection

# Create a metadata object
metadata = MetaData()

# Define your table schema
# Example: Define a 'users' table with columns 'id' and 'name'
users = Table('users', metadata,
              Column('id', Integer, primary_key=True),
              Column('name', String(50)))

# Create the table if it doesn't exist
users.drop(engine, checkfirst=True)
users.create(engine)
metadata.create_all(engine)

# Execute a simple command
# Example: Insert a record into the 'users' table
# insert_command = users.insert().values(name='John')
insert_sql = text("INSERT INTO users (name) VALUES (:name)")
compound_sql = """
           BEGIN TRANSACTION;
           INSERT INTO users (name) VALUES ('Mohit');
           CREATE TABLE channel AS SELECT * FROM users WHERE 0;
           SELECT name FROM users;
           COMMIT;
       """

start = time.time()
result = my_conn.executescript(compound_sql)
my_conn.commit()
final = time.time()
result = final-start

# Close the connection properly
connection.close()

print(result)

