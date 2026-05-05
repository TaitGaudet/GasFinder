USE gasdb;

CREATE TABLE IF NOT EXISTS stations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    distance_miles DECIMAL(5,2),
    regular_price DECIMAL(4,3),
    midgrade_price DECIMAL(4,3),
    premium_price DECIMAL(4,3),
    diesel_price DECIMAL(4,3),
    last_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

);

CREATE TABLE IF NOT EXISTS favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    station_id INT,
    added_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES stations(id)
);

CREATE TABLE IF NOT EXISTS price_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    station_id INT,
    fuel_type VARCHAR(20),
    price DECIMAL(4,3),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES stations(id)
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    preffered_fuel ENUM('Regular', 'Midgrade', 'Premium', 'Diesel') NOT NULL,
    car_make VARCHAR(100),
    car_model VARCHAR(100),
    car_year INT(4),
    tank_size DECIMAL(3,1),
    mpg DECIMAL(3,1),
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);