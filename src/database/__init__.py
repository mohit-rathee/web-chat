from .. import server, tables
from .models import users
from .database_utils import create_channel
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker

# Loading data from Main Database.
def load_database(Base,engine):
    inspector = inspect(engine)
    tbls = inspector.get_table_names()
    tables["app"]={'Len':len(tbls)}
    for tb in tbls:
        if tb.isdigit():
            tables["app"][int(tb)]=create_channel(tb, Base,users)
    # Recreating the session.
    Base.metadata.create_all(bind=engine)
    sqlsession=sessionmaker(bind=engine)
    server['app']=sqlsession()

