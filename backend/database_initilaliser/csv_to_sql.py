import pandas as pd
import io
from database_initialiser import connect_to_db
COLUMNS = [
    "latitude",
    "longitude",

    "acq_date",
    "acq_time",

    "frp",
    "brightness",
    "bright_t31",
    "hotspot_type",

    "instrument",
    "confidence",
    "scan",
    "track"
]


def universal_harmoniser(file_path, null_cols: list = None):
    df = pd.read_csv(file_path)
    if null_cols:
        for null_col in null_cols:
            df[null_col] = None

    df = df.rename(columns={
        "type": "hotspot_type"
    })
    return df[COLUMNS]


def save_fires(dataframe):
    database = connect_to_db()
    cursor = database.cursor()

    try:
        buffer = io.StringIO()
        dataframe.to_csv(buffer, index=False, header=False)
        buffer.seek(0)

        cursor.copy_expert('''
        COPY hotspots_data (
            latitude,
            longitude,
            acq_date,
            acq_time,
            frp,
            brightness,
            bright_t31,
            hotspot_type,
            instrument,
            confidence,
            scan,
            track
        )
        FROM STDIN
        WITH (FORMAT CSV);
        ''', buffer)

        cursor.execute('''
        UPDATE hotspots_data
        SET geo = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
        WHERE geo IS NULL;
        ''')
        database.commit()

    except Exception as e:
        database.rollback()
        print(f"Something went wrong. Please try again. Error data: {e}")

    finally:
        database.close()

# When dropping a database / establishing a new connection, uncomment the code below


save_fires(universal_harmoniser("_data/MODIS fl/modis nrt fl.csv", null_cols=["type"]))
save_fires(universal_harmoniser("_data/MODIS fl/modis archive fl.csv"))
save_fires(universal_harmoniser("_data/MODIS uz/modis nrt uz.csv", null_cols=["type"]))
save_fires(universal_harmoniser("_data/MODIS uz/modis archive uz.csv"))

save_fires(universal_harmoniser("_data/VIIRS combined fl/nrt viirs fl.csv", null_cols=["type"]))
save_fires(universal_harmoniser("_data/VIIRS combined fl/archive viirs fl.csv"))
save_fires(universal_harmoniser("_data/VIIRS combined uz/nrt viirs uz.csv", null_cols=["type"]))
save_fires(universal_harmoniser("_data/VIIRS combined uz/archive viirs uz.csv"))




