import psycopg2
import os


def create_db(user="postgres", password="123456"):
    """Create a local PostgreSQL database
    Args:
        user (str): Your PostgreSQL username. Defaults to 'postgres'.
        password (str): Your PostgreSQL password. Defaults to 'postgres'.
    """

    database = psycopg2.connect(
        host="localhost",
        port='5432',
        user=user,
        password=password,
        dbname='postgres'
    )

    database.autocommit = True
    cursor = database.cursor()
    cursor.execute('CREATE DATABASE tulip_fire_data;')

    database.close()


def connect_to_db(user="postgres", password="123456"):
    """Create a local PostgreSQL database
    Args:
        user (str): Your PostgreSQL username. Defaults to 'postgres'.
        password (str): Your PostgreSQL password. Defaults to 'postgres'.

    Returns:
        An active database 'tulip_fire_data'
    """
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return psycopg2.connect(database_url)
    else:
        database = psycopg2.connect(
            host="localhost",
            port='5432',
            user=user,
            password=password,
            dbname='tulip_fire_data'
        )
        return database


def create_table_fires():
    """
    Connection to PostgreSQL database and creation of a table 'hotspots_data'
    """
    database = connect_to_db()
    cursor = database.cursor()

    cursor.execute("""
    CREATE EXTENSION IF NOT EXISTS postgis;
    
    CREATE TABLE IF NOT EXISTS hotspots_data(
        id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        
        acq_date DATE NOT NULL,
        acq_time INTEGER,
        
        frp REAL,
        brightness REAL,
        bright_t31 REAL,
        hotspot_type SMALLINT,
        
        instrument TEXT,
        confidence TEXT,
        scan REAL,
        track REAL,        
        geo GEOMETRY(POINT, 4326) 
    );  
    """)
    database.commit()
    database.close()


def index_database():
    """
    Creates indexes for the table 'hotspots_data'
    :return:
    """
    database = connect_to_db()
    cursor = database.cursor()

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_fires_date
        ON hotspots_data (acq_date);

        CREATE INDEX IF NOT EXISTS idx_fires_geom
        ON hotspots_data USING GIST (geo);
        ''')
    database.commit()
    database.close()


# uncomment the following code when initialising a new local database
#
# create_db()
# create_table_fires()
# index_database()
