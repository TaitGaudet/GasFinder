import mysql.connector
import os

# Database connection config pulled from environment variables
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'database'),
    'user': os.environ.get('DB_USER', 'gasuser'),
    'password': os.environ.get('DB_PASSWORD', 'gaspassword'),
    'database': os.environ.get('DB_NAME', 'gasdb')
}


def get_db_connection():
    """
    Establishes and returns a connection to the MySQL database
    using the DB_CONFIG dictionary.

    Returns:
        mysql.connector.connection: An active database connection object.
    """
    connection = mysql.connector.connect(**DB_CONFIG)
    return connection


def clear_data(cursor):
    """
    Clears all existing data from the price_history, favorites, and
    stations tables before seeding, preventing duplicate entries on
    re-runs.

    Deletes in the correct order to respect foreign key constraints:
        1. price_history (references stations)
        2. favorites (references stations)
        3. stations

    Args:
        cursor: An active MySQL cursor object.
    """

    cursor.execute("DELETE FROM price_history")
    cursor.execute("DELETE FROM favorites")
    cursor.execute("DELETE FROM stations")


def seed_stations(cursor):
    """
    Inserts hardcoded gas station data for stations near West Point,
    NY 10997 into the stations table.

    Each station record includes:
        - name (str): The brand/name of the gas station.
        - address (str): The street address of the station.
        - latitude (float): The GPS latitude coordinate.
        - longitude (float): The GPS longitude coordinate.
        - distance_miles (float): Driving distance in miles from West Point.
        - regular_price (float): Current hardcoded price for regular fuel.
        - midgrade_price (float): Current hardcoded price for midgrade fuel.
        - premium_price (float): Current hardcoded price for premium fuel.
        - diesel_price (float): Current hardcoded price for diesel fuel.

    Stations to seed:
        - Cumberland Farms, Highland Falls, NY — 0.8 miles
        - Mobil, Highland Falls, NY — 1.1 miles
        - Shell, Fort Montgomery, NY — 2.3 miles
        - Citgo, Highlands, NY — 2.7 miles
        - Gulf, Cornwall, NY — 4.1 miles
        - Sunoco, Vails Gate, NY — 6.5 miles
        - BP, Newburgh, NY — 8.2 miles
        - Speedway, Newburgh, NY — 9.0 miles

    Args:
        cursor: An active MySQL cursor object.
    """
    stations = [
        ('Cumberland Farms', '206 Main St, Highland Falls, NY', 41.3634, -73.9846, 0.8, 3.159, 3.359, 3.559, 3.459),
        ('Mobil',            '254 Main St, Highland Falls, NY', 41.3651, -73.9831, 1.1, 3.199, 3.399, 3.599, 3.499),
        ('Shell',            '24 US-9W, Fort Montgomery, NY',   41.3371, -73.9873, 2.3, 3.179, 3.379, 3.579, 3.479),
        ('Citgo',            '10 Bridge Rd, Highlands, NY',     41.3558, -73.9946, 2.7, 3.139, 3.339, 3.539, 3.439),
        ('Gulf',             '340 Hudson St, Cornwall, NY',     41.4326, -74.0018, 4.1, 3.219, 3.419, 3.619, 3.519),
        ('Sunoco',           '406 Temple Hill Rd, Vails Gate',  41.4501, -74.0324, 6.5, 3.149, 3.349, 3.549, 3.449),
        ('BP',               '1202 Route 300, Newburgh, NY',    41.5034, -74.0104, 8.2, 3.109, 3.309, 3.509, 3.409),
        ('Speedway',         '24 N Plank Rd, Newburgh, NY',     41.5143, -74.0198, 9.0, 3.099, 3.299, 3.499, 3.399),
    ]
 
    sql = """
        INSERT INTO stations
            (name, address, latitude, longitude, distance_miles,
             regular_price, midgrade_price, premium_price, diesel_price)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
 
    cursor.executemany(sql, stations)
 


def seed_price_history(cursor):
    """
    Inserts hardcoded price history records into the price_history table
    for each station, simulating past price changes over time.

    For each station, inserts at least three historical price records
    across the four fuel types (regular, midgrade, premium, diesel),
    with slightly varying prices to simulate real fluctuation.

    Each record includes:
        - station_id (int): The ID of the station this record belongs to.
        - fuel_type (str): One of 'regular', 'midgrade', 'premium', 'diesel'.
        - price (float): The historical price per gallon.
        - recorded_at (str): The timestamp of when the price was recorded,
          in the format 'YYYY-MM-DD HH:MM:SS'.

    Args:
        cursor: An active MySQL cursor object.
    """
    history = [
        # Cumberland Farms (station_id = 1)
        (1, 'regular',  3.199, '2026-04-01 08:00:00'),
        (1, 'regular',  3.179, '2026-04-07 08:00:00'),
        (1, 'regular',  3.159, '2026-04-14 08:00:00'),
        (1, 'midgrade', 3.399, '2026-04-01 08:00:00'),
        (1, 'midgrade', 3.379, '2026-04-07 08:00:00'),
        (1, 'midgrade', 3.359, '2026-04-14 08:00:00'),
        (1, 'premium',  3.599, '2026-04-01 08:00:00'),
        (1, 'premium',  3.579, '2026-04-07 08:00:00'),
        (1, 'premium',  3.559, '2026-04-14 08:00:00'),
        (1, 'diesel',   3.499, '2026-04-01 08:00:00'),
        (1, 'diesel',   3.479, '2026-04-07 08:00:00'),
        (1, 'diesel',   3.459, '2026-04-14 08:00:00'),
 
        # Mobil (station_id = 2)
        (2, 'regular',  3.239, '2026-04-01 08:00:00'),
        (2, 'regular',  3.219, '2026-04-07 08:00:00'),
        (2, 'regular',  3.199, '2026-04-14 08:00:00'),
        (2, 'midgrade', 3.439, '2026-04-01 08:00:00'),
        (2, 'midgrade', 3.419, '2026-04-07 08:00:00'),
        (2, 'midgrade', 3.399, '2026-04-14 08:00:00'),
        (2, 'premium',  3.639, '2026-04-01 08:00:00'),
        (2, 'premium',  3.619, '2026-04-07 08:00:00'),
        (2, 'premium',  3.599, '2026-04-14 08:00:00'),
        (2, 'diesel',   3.539, '2026-04-01 08:00:00'),
        (2, 'diesel',   3.519, '2026-04-07 08:00:00'),
        (2, 'diesel',   3.499, '2026-04-14 08:00:00'),
 
        # Shell (station_id = 3)
        (3, 'regular',  3.219, '2026-04-01 08:00:00'),
        (3, 'regular',  3.199, '2026-04-07 08:00:00'),
        (3, 'regular',  3.179, '2026-04-14 08:00:00'),
        (3, 'midgrade', 3.419, '2026-04-01 08:00:00'),
        (3, 'midgrade', 3.399, '2026-04-07 08:00:00'),
        (3, 'midgrade', 3.379, '2026-04-14 08:00:00'),
        (3, 'premium',  3.619, '2026-04-01 08:00:00'),
        (3, 'premium',  3.599, '2026-04-07 08:00:00'),
        (3, 'premium',  3.579, '2026-04-14 08:00:00'),
        (3, 'diesel',   3.519, '2026-04-01 08:00:00'),
        (3, 'diesel',   3.499, '2026-04-07 08:00:00'),
        (3, 'diesel',   3.479, '2026-04-14 08:00:00'),
 
        # Citgo (station_id = 4)
        (4, 'regular',  3.179, '2026-04-01 08:00:00'),
        (4, 'regular',  3.159, '2026-04-07 08:00:00'),
        (4, 'regular',  3.139, '2026-04-14 08:00:00'),
        (4, 'midgrade', 3.379, '2026-04-01 08:00:00'),
        (4, 'midgrade', 3.359, '2026-04-07 08:00:00'),
        (4, 'midgrade', 3.339, '2026-04-14 08:00:00'),
        (4, 'premium',  3.579, '2026-04-01 08:00:00'),
        (4, 'premium',  3.559, '2026-04-07 08:00:00'),
        (4, 'premium',  3.539, '2026-04-14 08:00:00'),
        (4, 'diesel',   3.479, '2026-04-01 08:00:00'),
        (4, 'diesel',   3.459, '2026-04-07 08:00:00'),
        (4, 'diesel',   3.439, '2026-04-14 08:00:00'),
 
        # Gulf (station_id = 5)
        (5, 'regular',  3.259, '2026-04-01 08:00:00'),
        (5, 'regular',  3.239, '2026-04-07 08:00:00'),
        (5, 'regular',  3.219, '2026-04-14 08:00:00'),
        (5, 'midgrade', 3.459, '2026-04-01 08:00:00'),
        (5, 'midgrade', 3.439, '2026-04-07 08:00:00'),
        (5, 'midgrade', 3.419, '2026-04-14 08:00:00'),
        (5, 'premium',  3.659, '2026-04-01 08:00:00'),
        (5, 'premium',  3.639, '2026-04-07 08:00:00'),
        (5, 'premium',  3.619, '2026-04-14 08:00:00'),
        (5, 'diesel',   3.559, '2026-04-01 08:00:00'),
        (5, 'diesel',   3.539, '2026-04-07 08:00:00'),
        (5, 'diesel',   3.519, '2026-04-14 08:00:00'),
 
        # Sunoco (station_id = 6)
        (6, 'regular',  3.189, '2026-04-01 08:00:00'),
        (6, 'regular',  3.169, '2026-04-07 08:00:00'),
        (6, 'regular',  3.149, '2026-04-14 08:00:00'),
        (6, 'midgrade', 3.389, '2026-04-01 08:00:00'),
        (6, 'midgrade', 3.369, '2026-04-07 08:00:00'),
        (6, 'midgrade', 3.349, '2026-04-14 08:00:00'),
        (6, 'premium',  3.589, '2026-04-01 08:00:00'),
        (6, 'premium',  3.569, '2026-04-07 08:00:00'),
        (6, 'premium',  3.549, '2026-04-14 08:00:00'),
        (6, 'diesel',   3.489, '2026-04-01 08:00:00'),
        (6, 'diesel',   3.469, '2026-04-07 08:00:00'),
        (6, 'diesel',   3.449, '2026-04-14 08:00:00'),
 
        # BP (station_id = 7)
        (7, 'regular',  3.149, '2026-04-01 08:00:00'),
        (7, 'regular',  3.129, '2026-04-07 08:00:00'),
        (7, 'regular',  3.109, '2026-04-14 08:00:00'),
        (7, 'midgrade', 3.349, '2026-04-01 08:00:00'),
        (7, 'midgrade', 3.329, '2026-04-07 08:00:00'),
        (7, 'midgrade', 3.309, '2026-04-14 08:00:00'),
        (7, 'premium',  3.549, '2026-04-01 08:00:00'),
        (7, 'premium',  3.529, '2026-04-07 08:00:00'),
        (7, 'premium',  3.509, '2026-04-14 08:00:00'),
        (7, 'diesel',   3.449, '2026-04-01 08:00:00'),
        (7, 'diesel',   3.429, '2026-04-07 08:00:00'),
        (7, 'diesel',   3.409, '2026-04-14 08:00:00'),
 
        # Speedway (station_id = 8)
        (8, 'regular',  3.139, '2026-04-01 08:00:00'),
        (8, 'regular',  3.119, '2026-04-07 08:00:00'),
        (8, 'regular',  3.099, '2026-04-14 08:00:00'),
        (8, 'midgrade', 3.339, '2026-04-01 08:00:00'),
        (8, 'midgrade', 3.319, '2026-04-07 08:00:00'),
        (8, 'midgrade', 3.299, '2026-04-14 08:00:00'),
        (8, 'premium',  3.539, '2026-04-01 08:00:00'),
        (8, 'premium',  3.519, '2026-04-07 08:00:00'),
        (8, 'premium',  3.499, '2026-04-14 08:00:00'),
        (8, 'diesel',   3.439, '2026-04-01 08:00:00'),
        (8, 'diesel',   3.419, '2026-04-07 08:00:00'),
        (8, 'diesel',   3.399, '2026-04-14 08:00:00'),
    ]
 
    sql = """
        INSERT INTO price_history (station_id, fuel_type, price, recorded_at)
        VALUES (%s, %s, %s, %s)
    """
 
    cursor.executemany(sql, history)


def main():
    """
    Entry point for the seed script. Orchestrates the full seeding process
    in the following order:

        1. Establish a database connection.
        2. Create a cursor.
        3. Call clear_data() to remove any existing records.
        4. Call seed_stations() to insert station data.
        5. Call seed_price_history() to insert historical price data.
        6. Commit all changes to the database.
        7. Close the cursor and connection.

    Prints a confirmation message after each major step so progress
    can be tracked when the script is run.
    """

    print("Establishing Connection")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    print("Established Cursor")

    try:
        clear_data(cursor)
        print("Cleared Data")


        seed_stations(cursor)
        print("Stations Seeded")

        seed_price_history(cursor)
        print("Price History Complete")

        conn.commit()
        print("Committed to database")

    except Exception as e:
        conn.rollback()
        print(f"Seeding Failed: {e}")
    
    finally:
        cursor.close()
        conn.close()




if __name__ == '__main__':
    """
    Runs the main() function when the script is executed directly.
    """
    main()