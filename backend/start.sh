#!/bin/bash
echo "Waiting for database to be ready..."

until python -c "import mysql.connector; mysql.connector.connect(host='database', user='gasuser', password='gaspass', database='gasdb')" 2>/dev/null; do
    echo "Database not ready yet, retrying in 3 seconds..."
    sleep 3
done

echo "Database is ready!"

# Check if stations table is empty
STATION_COUNT=$(python -c "
import mysql.connector
conn = mysql.connector.connect(host='database', user='gasuser', password='gaspass', database='gasdb')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM stations')
print(cursor.fetchone()[0])
conn.close()
")

if [ "$STATION_COUNT" -eq "0" ]; then
    echo "Database is empty, seeding..."
    python seed.py
else
    echo "Database already seeded ($STATION_COUNT stations found), skipping seed."
fi

echo "Starting Flask..."
python app.py