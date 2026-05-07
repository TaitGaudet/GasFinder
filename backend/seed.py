import mysql.connector
import os
import random

# Database connection config pulled from environment variables
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'database'),
    'user': os.environ.get('DB_USER', 'gasuser'),
    'password': os.environ.get('DB_PASSWORD', 'gaspass'),
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


def random_price(base, spread=0.20):
    """
    Generates a randomized price within a realistic range.

    Args:
        base (float): The base price to start from.
        spread (float): The maximum amount to add above the base.

    Returns:
        float: A rounded price to 3 decimal places.
    """
    return round(random.uniform(base, base + spread), 3)


def seed_stations(cursor):
    """
    Inserts gas station data for stations near West Point, NY 10997
    into the stations table with realistic current prices in the
    $4.00 - $5.00 range, with random variation per station.

    Each station record includes:
        - name (str): The brand/name of the gas station.
        - address (str): The street address of the station.
        - latitude (float): The GPS latitude coordinate.
        - longitude (float): The GPS longitude coordinate.
        - distance_miles (float): Driving distance in miles from West Point.
        - regular_price (float): Current price for regular fuel.
        - midgrade_price (float): Current price for midgrade fuel.
        - premium_price (float): Current price for premium fuel.
        - diesel_price (float): Current price for diesel fuel.

    Stations seeded:
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
    station_data = [
        ('Cumberland Farms', '206 Main St, Highland Falls, NY', 41.3634, -73.9846, 0.8),
        ('Mobil',            '254 Main St, Highland Falls, NY', 41.3651, -73.9831, 1.1),
        ('Shell',            '24 US-9W, Fort Montgomery, NY',   41.3371, -73.9873, 2.3),
        ('Citgo',            '10 Bridge Rd, Highlands, NY',     41.3558, -73.9946, 2.7),
        ('Gulf',             '340 Hudson St, Cornwall, NY',     41.4326, -74.0018, 4.1),
        ('Sunoco',           '406 Temple Hill Rd, Vails Gate',  41.4501, -74.0324, 6.5),
        ('BP',               '1202 Route 300, Newburgh, NY',    41.5034, -74.0104, 8.2),
        ('Speedway',         '24 N Plank Rd, Newburgh, NY',     41.5143, -74.0198, 9.0),
    ]

    stations = []
    for s in station_data:
        regular  = random_price(4.099, 0.30)
        midgrade = round(regular  + random_price(0.20, 0.10), 3)
        premium  = round(midgrade + random_price(0.20, 0.10), 3)
        diesel   = round(regular  + random_price(0.15, 0.20), 3)
        stations.append((*s, regular, midgrade, premium, diesel))

    sql = """
        INSERT INTO stations
            (name, address, latitude, longitude, distance_miles,
             regular_price, midgrade_price, premium_price, diesel_price)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.executemany(sql, stations)
    return stations


def seed_price_history(cursor, stations):
    """
    Inserts price history records into the price_history table for each
    station, simulating realistic price changes over the past 6 weeks
    trending from ~$4.50+ down toward current prices.

    For each station, inserts three historical price records per fuel
    type showing a gradual downward trend to the current seeded price.

    Each record includes:
        - station_id (int): The ID of the station this record belongs to.
        - fuel_type (str): One of 'regular', 'midgrade', 'premium', 'diesel'.
        - price (float): The historical price per gallon.
        - recorded_at (str): Timestamp in 'YYYY-MM-DD HH:MM:SS' format.

    Args:
        cursor: An active MySQL cursor object.
        stations (list): List of station tuples returned by seed_stations(),
                         used to base history prices on current prices.
    """
    history = []
    dates = ['2026-03-17 08:00:00', '2026-04-07 08:00:00', '2026-04-28 08:00:00']

    for i, station in enumerate(stations):
        station_id = i + 1
        regular  = station[5]
        midgrade = station[6]
        premium  = station[7]
        diesel   = station[8]

        for fuel_type, current_price in [
            ('regular',  regular),
            ('midgrade', midgrade),
            ('premium',  premium),
            ('diesel',   diesel),
        ]:
            # Work backwards — oldest price is highest, trending down to current
            old_price  = round(current_price + random_price(0.30, 0.20), 3)
            mid_price  = round(current_price + random_price(0.10, 0.15), 3)
            curr_price = current_price

            history.append((station_id, fuel_type, old_price,  dates[0]))
            history.append((station_id, fuel_type, mid_price,  dates[1]))
            history.append((station_id, fuel_type, curr_price, dates[2]))

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

        stations = seed_stations(cursor)
        print("Stations Seeded")

        seed_price_history(cursor, stations)
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