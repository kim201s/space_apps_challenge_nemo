from fastapi import FastAPI
from backend.database_initilaliser.database_initialiser import connect_to_db
from backend.database_initilaliser.csv_to_sql import COLUMNS
from fastapi.middleware.cors import CORSMiddleware
from backend.api_requester.forecaster import forecast_modelling

app = FastAPI()

app.add_middleware(
    CORSMiddleware,     # type: ignore
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/fires")
def get_fires(date, min_lon: float, min_lat: float, max_lon: float, max_lat: float):
    database = connect_to_db()
    cursor = database.cursor()

    try:
        cursor.execute(f"""
        SELECT id, {", ".join(COLUMNS)} FROM hotspots_data
        WHERE acq_date = %s 
        AND ST_Within(geo, ST_MakeEnvelope(%s, %s, %s, %s, 4326));
        """, (date, min_lon, min_lat, max_lon, max_lat))

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        fires = [dict(zip(columns, row)) for row in rows]
        return {"fires": fires}

    except:
        database.rollback()
        return {}

    finally:
        database.close()


@app.get("/fire_stats")
def get_fire_stats(min_date, max_date, interval, min_lon: float, min_lat: float, max_lon: float, max_lat: float):
    database = connect_to_db()
    query_dict = {
        "min_date": min_date,
        "max_date": max_date,
        "interval": interval,
        "min_lon": min_lon,
        "min_lat": min_lat,
        "max_lon": max_lon,
        "max_lat": max_lat
    }
    cursor = database.cursor()
    try:
        cursor.execute("""
        WITH date_series AS (
            SELECT generate_series(
            %(min_date)s::date,
            %(max_date)s::date,
            (%(interval)s::text || ' days')::interval
                ) ::date AS start_point
            ),
            
        binned_data AS (
        SELECT
             FLOOR((acq_date - %(min_date)s) / %(interval)s) AS bucket_index,
             COUNT(*) AS bucket_fire_count,
             AVG(frp) AS mean_frp,
             SUM(frp) AS total_frp
             
        FROM hotspots_data
        
        WHERE acq_date >= %(min_date)s 
            AND acq_date <= %(max_date)s
            AND ST_Within(geo, ST_MakeEnvelope(%(min_lon)s, %(min_lat)s, %(max_lon)s, %(max_lat)s, 4326))
            
        GROUP BY FLOOR((acq_date - %(min_date)s) / %(interval)s)
        )    
        
        SELECT 
            ds.start_point,    
            LEAST(
                ds.start_point + %(interval)s::integer - 1,
                %(max_date)s::date
            ) AS end_point,
            
        COALESCE(binned_data.bucket_fire_count, 0) AS bucket_fire_count,
        COALESCE(binned_data.total_frp, 0) AS total_frp,
        COALESCE(binned_data.mean_frp, 0) AS mean_frp

        FROM date_series ds
        LEFT JOIN binned_data
            ON binned_data.bucket_index = FLOOR((ds.start_point - %(min_date)s::date) / %(interval)s)

            ORDER BY ds.start_point;
        """, query_dict)

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        stats = [dict(zip(columns, row)) for row in rows]
        means = [dict_fire["mean_frp"] for dict_fire in stats]
        sums = [dict_fire["total_frp"] for dict_fire in stats]
        counts = [dict_fire["bucket_fire_count"] for dict_fire in stats]
        return {
            "statistics": stats,
            "mean_frp_values": means,
            "sum_frp_values": sums,
            "hotspot_count": counts
        }

    except:
        database.rollback()
        return {}

    finally:
        database.close()


@app.get("/fires_gridview")
def get_grid_fires(date, min_lon: float, min_lat: float, max_lon: float, max_lat: float):
    database = connect_to_db()
    cursor = database.cursor()

    try:
        cursor.execute(f"""
        SELECT 
            COUNT(id),
            ST_XMin(
                ST_Transform(ST_Expand(ST_SnapToGrid(ST_Transform(geo, 3857), 1000), 500), 4326)
            ) AS sector_minx, 
            ST_YMin(
                ST_Transform(ST_Expand(ST_SnapToGrid(ST_Transform(geo, 3857), 1000), 500), 4326)
            ) AS sector_miny,
            ST_XMax(
                ST_Transform(ST_Expand(ST_SnapToGrid(ST_Transform(geo, 3857), 1000), 500), 4326)
            ) AS sector_maxx,
            ST_YMax(
                ST_Transform(ST_Expand(ST_SnapToGrid(ST_Transform(geo, 3857), 1000), 500), 4326)
            ) AS sector_maxy

        FROM hotspots_data 
        WHERE acq_date = %s
        AND ST_Within(geo, ST_MakeEnvelope(%s, %s, %s, %s, 4326))

        GROUP BY ST_SnapToGrid(ST_Transform(geo, 3857), 1000);
        """, (date, min_lon, min_lat, max_lon, max_lat))

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        stats = [dict(zip(columns, row)) for row in rows]
        return {"fires": rows,
                "stats": stats}

    except:
        database.rollback()
        return {}

    finally:
        database.close()


@app.get("/forecast")
def fires_forecast(
    max_date: str,
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    min_date: str = "2016-01-01",
    forecast_duration: int = 12,
    period: float = 12,
    harmonics_count: int = 2,
    interval: int = 30
):

    stats = get_fire_stats(min_date, max_date, interval, min_lon, min_lat, max_lon, max_lat)
    sum_values = [round(i,2) for i in stats["sum_frp_values"]]
    return {
        "sum_frp_forecast":
            forecast_modelling(
                sum_values,
                forecast_duration,
                max_date,
                period,
                harmonics_count
            )}
