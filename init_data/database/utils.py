import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

HOST = 'postgres'
USERNAME = os.getenv('SERVICE_DB_USERNAME')
PASSWORD = os.getenv('SERVICE_DB_PWD')
DBNAME = os.getenv('SERVICE_DB_NAME')

pgconfig = {'pguser':USERNAME,
            'pgpasswd':PASSWORD,
            'pghost':HOST,
            'pgport':5432,
            'pgdb':DBNAME}

def get_engine(user, passwd, host, port, db) :
    url = f'postgresql://{user}:{passwd}@{host}:{port}/{db}'

    engine = create_engine(url, pool_size=50, echo=False)
    return engine

def get_engine_from_pgconfig():
    keys = {'pguser', 'pgpasswd', 'pghost', 'pgport', 'pgdb'}
    if not all( key in keys for key in pgconfig ):
        raise Exception('Bad Config file')
    
    return get_engine(pgconfig['pguser'], pgconfig['pgpasswd'], pgconfig['pghost'], pgconfig['pgport'], pgconfig['pgdb'])

def get_session():
    engine = get_engine_from_pgconfig()
    session = sessionmaker(bind=engine)

    return session()

def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()
