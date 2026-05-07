from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import os
from flask import Flask, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

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

# ─────────────────────────────────────────────
# STATION ROUTES
# ─────────────────────────────────────────────

@app.route('/api/stations', methods=['GET'])
def get_stations():
    """
    Retrieves all gas stations from the stations table in the database.

    Queries all columns for every station and returns them as a JSON array.

    Returns:
        JSON: A list of all gas station objects, each containing id, name,
        address, latitude, longitude, distance_miles, regular_price,
        midgrade_price, premium_price, diesel_price, and last_updated.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM stations")
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(results)

@app.route('/api/stations/<int:station_id>', methods=['GET'])
def get_station(station_id):
    """
    Retrieves a single gas station by its ID from the database.

    Args:
        station_id (int): The unique ID of the station from the URL path.

    Returns:
        JSON: A single gas station object if found.
        404: A JSON error message if no station with that ID exists.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM stations WHERE id= %s", (station_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'Station not found'}), 404


# ─────────────────────────────────────────────
# FILTER ROUTE
# ─────────────────────────────────────────────

@app.route('/api/stations/filter', methods=['GET'])
def filter_stations():
    """
    Filters gas stations based on optional query parameters provided by
    the user.

    Accepts the following optional query parameters:
        - max_price (float): Maximum price per gallon to filter by.
        - max_distance (float): Maximum distance in miles from West Point.
        - fuel_type (str): Fuel type to sort/filter by. Accepted values are
          'regular', 'midgrade', 'premium', 'diesel'.

    Builds a dynamic SQL query using only the parameters that were provided,
    ignoring any that are missing.

    Returns:
        JSON: A filtered list of gas station objects matching the criteria.
        400: A JSON error message if an invalid fuel_type is provided.
    """
    max_price = request.args.get('max_price')
    max_distance = request.args.get('max_distance')
    fuel_type = request.args.get('fuel_type')

    valid_fuel_types = ['regular', 'midgrade', 'premium', 'diesel']

    if fuel_type and fuel_type not in valid_fuel_types:
        return jsonify({'error': 'Invalid fuel type'}), 400
    
    query = "SELECT * FROM stations"
    conditions = []
    values = []

    if max_price:
        conditions.append("regular_price <= %s")
        values.append(float(max_price))
    
    if max_distance:
        conditions.append("distance_miles <= %s")
        values.append(float(max_distance))
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    if fuel_type:
        query += " ORDER BY " + fuel_type + "_price ASC"
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(query, values)
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return(jsonify(result))


# ─────────────────────────────────────────────
# RECOMMENDATION ROUTE
# ─────────────────────────────────────────────

@app.route('/api/stations/recommend', methods=['GET'])
def recommend():
    """
    Recommends the best gas station based on a combined score of price
    and distance.

    Accepts the following optional query parameter:
        - fuel_type (str): The fuel type to base the recommendation on.
          Defaults to 'regular' if not provided.

    Scoring formula:
        score = price + (distance_miles * 0.1)

    A lower score is better. The station with the lowest score is returned
    as the recommendation.

    Returns:
        JSON: A single gas station object representing the best option,
        along with its calculated score.
        404: A JSON error message if no stations are found.
    """

    max_price = request.args.get('max_price')
    max_distance = request.args.get('max_distance')
    fuel_type = request.args.get('fuel_type')

    valid_fuel_types = ['regular', 'midgrade', 'premium', 'diesel']

    if fuel_type and fuel_type not in valid_fuel_types:
        return jsonify({'error': 'Invalid fuel type'}), 400
    
    query = "SELECT * FROM stations"
    conditions = []
    values = []

    if max_price:
        conditions.append("regular_price <= %s")
        values.append(float(max_price))
    
    if max_distance:
        conditions.append("distance_miles <= %s")
        values.append(float(max_distance))
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    if fuel_type:
        query += " ORDER BY " + fuel_type + "_price ASC"
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(query, values)
    stations = cursor.fetchall()

    gas_list = []
    
    price = fuel_type + '_price'

    for station in stations:
        score = float(station[price]) + (float(station['distance_miles']) * 0.1)
        score_tup = (station, score)
        gas_list.append(score_tup)
    
    lowest_tup = None
    for gas in gas_list:
        if lowest_tup is None or gas[1] < lowest_tup[1]:
            lowest_tup = gas
    
    cursor.close()
    conn.close()
    

    if lowest_tup is None:
        return jsonify({'error': 'No stations found'}), 404
    
    return jsonify(lowest_tup[0])

# ─────────────────────────────────────────────
# FAVORITES ROUTES
# ─────────────────────────────────────────────

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    """
    Retrieves all gas stations that have been saved as favorites.

    Performs a JOIN between the favorites table and the stations table
    to return full station details, not just IDs.

    Returns:
        JSON: A list of gas station objects that are marked as favorites,
        each including the date they were added via added_on.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT stations.*, favorites.added_on
        FROM favorites
        JOIN stations ON favorites.station_id = stations.id
    """)
    

    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(results)


@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    """
    Adds a gas station to the favorites table.

    Expects a JSON request body with the following field:
        - station_id (int): The ID of the station to favorite.

    Checks that the station exists before inserting. Prevents duplicate
    favorites by checking if the station is already in the favorites table.

    Returns:
        JSON: A success message if the station was added.
        400: A JSON error message if station_id is missing from the request.
        404: A JSON error message if the station does not exist.
        409: A JSON error message if the station is already a favorite.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    station_id = request.json.get('station_id')

    if not station_id:
        return jsonify({'error': 'station_id is required'}), 400

    cursor.execute("SELECT id FROM stations WHERE id = %s", (station_id,))
    result = cursor.fetchone()

    if not result:
        return jsonify({'error': 'Station not found'}), 404
    
    cursor.execute("SELECT id FROM favorites WHERE station_id = %s", (station_id,))
    duplicate = cursor.fetchone()

    if duplicate:
        return jsonify({'error': 'Station is already a favorite'}), 409

    cursor.execute("INSERT INTO favorites (station_id) VALUES (%s)", (station_id,))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Station added to favorites!'})


@app.route('/api/favorites/<int:station_id>', methods=['DELETE'])
def remove_favorite(station_id):
    """
    Removes a gas station from the favorites table by its station ID.

    Args:
        station_id (int): The unique ID of the station to remove from
        favorites, taken from the URL path.

    Returns:
        JSON: A success message if the favorite was removed.
        404: A JSON error message if the station was not in favorites.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM favorites WHERE station_id = %s", (station_id,))
    result = cursor.fetchone()

    if not result:
        return jsonify({'error': 'Station not found'}), 404

    cursor.execute("DELETE FROM favorites WHERE station_id = %s", (station_id,))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Station removed from favorites!'})


# ─────────────────────────────────────────────
# PRICE HISTORY ROUTE
# ─────────────────────────────────────────────

@app.route('/api/stations/<int:station_id>/history', methods=['GET'])
def get_price_history(station_id):
    """
    Retrieves the price history for a specific gas station.

    Queries the price_history table for all entries matching the given
    station_id, ordered by recorded_at descending so the most recent
    prices appear first.

    Args:
        station_id (int): The unique ID of the station from the URL path.

    Returns:
        JSON: A list of price history records for that station, each
        containing fuel_type, price, and recorded_at timestamp.
        404: A JSON error if the station does not exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT fuel_type, price, recorded_at FROM price_history WHERE station_id = %s ORDER BY recorded_at DESC", (station_id,))
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    if not result:
        return jsonify({'error': 'No price history found for this station'}), 404

    

    return jsonify(result)

# ─────────────────────────────────────────────
# User Creation
# ─────────────────────────────────────────────


@app.route('/api/register', methods=['POST'])
def register_user():
    username = request.form.get('username')
    password = request.form.get('password')
    fuel = request.form.get('preffered_fuel')
    make = request.form.get('car_make')
    model = request.form.get('car_model')
    
    year = request.form.get('car_year') or None
    tank = request.form.get('tank_size') or None
    mpg = request.form.get('mpg') or None

    hashed_pw = generate_password_hash(password)

    sql_query = """
        INSERT INTO users 
        (username, password_hash, preffered_fuel, car_make, car_model, car_year, tank_size, mpg)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    sql_values = (username, hashed_pw, fuel, make, model, year, tank, mpg)

    # We need to actually open the database connection here!
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Execute and commit the save to the database
        cursor.execute(sql_query, sql_values)
        conn.commit()
        
        # Close connections
        cursor.close()
        conn.close()
        
        # Return a success JSON response
        return jsonify({"message": f"Profile created for {username}", "username": username}), 200
    
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({"error": f"Error registering: {str(e)}"}), 400
    
    
@app.route('/api/login', methods=['POST'])
def login_user():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Look up the user by their username
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        # If the user exists AND the password matches the saved hash...
        if user and check_password_hash(user['password_hash'], password):
            return jsonify({"message": "Login successful", "username": username}), 200
        else:
            return jsonify({"error": "Invalid username or password."}), 401
            
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == '__main__':
    """
    Starts the Flask development server.

    Runs on host 0.0.0.0 so it is accessible from outside the container,
    on port 5000. Debug mode is controlled by the DEBUG environment
    variable and should be set to False in production.
    """
    debug_mode = os.environ.get('DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)