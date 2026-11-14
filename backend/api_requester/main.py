from fastapi import FastAPI
from backend.database_initilaliser.database_initialiser import connect_to_db
from backend.database_initilaliser.csv_to_sql import COLUMNS
from fastapi.middleware.cors import CORSMiddleware

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
def get_fire_stats(min_date, max_date, interval):
    database = connect_to_db()
    query_dict = {
        "min_date": min_date,
        "max_date": max_date,
        "interval": interval
    }
    cursor = database.cursor()
    try:
        cursor.execute(f"""WITH binned_data AS (
        SELECT 
            FLOOR((acq_date - %(min_date)s) / %(interval)s) AS bucket_index,
            COUNT(*) AS bucket_fire_count, 
            AVG(frp) AS mean_frp,
            SUM(frp) AS total_frp
        FROM hotspots_data
        WHERE acq_date >= %(min_date)s AND acq_date <= %(max_date)s
        GROUP BY FLOOR((acq_date - %(min_date)s) / %(interval)s)
        )

        SELECT 
            bucket_index,
            ( %(min_date)s::date + (bucket_index * %(interval)s)::integer ) AS start_point,
            (( %(min_date)s::date + (bucket_index * %(interval)s)::integer ) + %(interval)s::integer - 1) AS end_point,
            bucket_fire_count,
            total_frp,
            mean_frp
        FROM binned_data
        ORDER BY bucket_index;
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


# AND ST_Within(geo, ST_MakeEnvelope(10, 10, 60, 60, 4326))

@app.get("/fires_gridview")
def get_fires(date, min_lon: float, min_lat: float, max_lon: float, max_lat: float):
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
