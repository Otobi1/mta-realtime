import os
import pandas as pd
import psycopg2

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USERNAME")
POSTGRES_PASS = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

# Paths to the unzipped GTFS data
GTFS_DIR = "gtfs_subway"
GTFS_SUPP_DIR = "gtfs_supplemented"


def create_tables(conn):
    """
    Create minimal tables for GTFS data.
    You can expand these schemas as needed (indexes, constraints, etc.).
    """
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS routes (
                route_id TEXT PRIMARY KEY,
                route_short_name TEXT,
                route_long_name TEXT,
                route_type TEXT
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS stops (
                stop_id TEXT PRIMARY KEY,
                stop_name TEXT,
                stop_lat TEXT,
                stop_lon TEXT,
                location_type TEXT
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                trip_id TEXT PRIMARY KEY,
                route_id TEXT,
                service_id TEXT,
                trip_headsign TEXT,
                direction_id TEXT
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS stop_times (
                trip_id TEXT,
                arrival_time TEXT,
                departure_time TEXT,
                stop_id TEXT,
                stop_sequence TEXT
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS calendar (
                service_id TEXT PRIMARY KEY,
                monday TEXT,
                tuesday TEXT,
                wednesday TEXT,
                thursday TEXT,
                friday TEXT,
                saturday TEXT,
                sunday TEXT,
                start_date TEXT,
                end_date TEXT
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS calendar_dates (
                service_id TEXT,
                date TEXT,
                exception_type TEXT,
                FOREIGN KEY (service_id) REFERENCES calendar(service_id)
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS agency (
                agency_id TEXT PRIMARY KEY,
                agency_name TEXT,
                agency_url TEXT,
                agency_timezone TEXT
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS shapes (
            shape_id TEXT,
            shape_pt_lat TEXT,
            shape_pt_lon TEXT,
            shape_pt_sequence TEXT
            );
    """)
        cur.execute("""
           CREATE TABLE IF NOT EXISTS transfers (
            from_stop_id TEXT,
            to_stop_id TEXT,
            transfer_type TEXT,
            min_transfer_time TEXT
            );
        """)
        conn.commit()


def load_csv_to_db(conn, csv_path, table_name, columns):
    """
    Helper to load a CSV into Postgres using pandas.
    columns is a list of columns we expect in the CSV for the table.
    """
    df = pd.read_csv(csv_path, usecols=columns)

    # Drop duplicates by the first column in 'columns'
    df = df.drop_duplicates(subset=[columns[0]])

    # Convert any int64 columns to Python's built-in str
    for col in df.select_dtypes(include=["int64"]).columns:
        df[col] = df[col].astype(str)

    # Also ensure everything is stored as Python objects (not NumPy dtypes)
    # This will force each cell to be a Python object, not a NumPy scalar.
    df = df.astype(object)

    # Convert df into a list of tuples (pure Python)
    values = [tuple(row) for row in df.to_numpy(dtype=object)]

    with conn.cursor() as cur:
        placeholder = ", ".join(["%s"] * len(columns))
        cols = ", ".join(columns)
        insert_query = (
            f"INSERT INTO {table_name} ({cols}) "
            f"VALUES ({placeholder}) ON CONFLICT DO NOTHING;"
        )
        for val in values:
            cur.execute(insert_query, val)
    conn.commit()


def main():
    conn = psycopg2.connect(
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASS,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT
    )

    create_tables(conn)

    # Load routes
    load_csv_to_db(
        conn,
        f"{GTFS_DIR}/routes.txt",
        "routes",
        ["route_id", "route_short_name", "route_long_name", "route_type"]
    )

    # Load stops
    load_csv_to_db(
        conn,
        f"{GTFS_DIR}/stops.txt",
        "stops",
        ["stop_id", "stop_name", "stop_lat", "stop_lon", "location_type"]
    )

    # Load trips
    load_csv_to_db(
        conn,
        f"{GTFS_DIR}/trips.txt",
        "trips",
        ["trip_id", "route_id", "service_id", "trip_headsign", "direction_id"]
    )

    # Load stop_times
    load_csv_to_db(
        conn,
        f"{GTFS_DIR}/stop_times.txt",
        "stop_times",
        ["trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence"]
    )

    # Load calendar
    load_csv_to_db(
        conn,
        f"{GTFS_DIR}/calendar.txt",
        "calendar",
        ["service_id", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "start_date", "end_date"]
    )

    # Load calendar_dates
    load_csv_to_db(
        conn,
        f"{GTFS_DIR}/calendar_dates.txt",
        "calendar_dates",
        ["service_id", "date", "exception_type"]
    )

    # Load agency
    load_csv_to_db(
        conn,
        f"{GTFS_DIR}/agency.txt",
        "agency",
        ["agency_id", "agency_name", "agency_url", "agency_timezone"]
    )

    # Load shapes
    load_csv_to_db(
        conn,
        f"{GTFS_DIR}/shapes.txt",
        "shapes",
        ["shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"]
    )

    # Load transfers
    load_csv_to_db(
        conn,
        f"{GTFS_DIR}/transfers.txt",
        table_name="transfers",
        columns=["from_stop_id", "to_stop_id", "transfer_type", "min_transfer_time"]
    )

    conn.close()

if __name__ == "__main__":
    main()