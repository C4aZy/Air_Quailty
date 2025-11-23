import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('data/cleanair.db')
    cursor = conn.cursor()
    
    # Table for community reports
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            pollution_type TEXT NOT NULL,
            description TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table for cached air quality data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS air_quality (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            aqi INTEGER NOT NULL,
            pm25 REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_report(location, lat, lon, pollution_type, description):
    conn = sqlite3.connect('data/cleanair.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reports (location, latitude, longitude, pollution_type, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (location, lat, lon, pollution_type, description))
    conn.commit()
    conn.close()

def get_all_reports():
    conn = sqlite3.connect('data/cleanair.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reports ORDER BY timestamp DESC')
    reports = cursor.fetchall()
    conn.close()
    return reports

def save_air_quality(city, aqi, pm25):
    conn = sqlite3.connect('data/cleanair.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO air_quality (city, aqi, pm25)
        VALUES (?, ?, ?)
    ''', (city, aqi, pm25))
    conn.commit()
    conn.close()

def get_air_quality_history(city, limit=10):
    conn = sqlite3.connect('data/cleanair.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT aqi, pm25, timestamp FROM air_quality 
        WHERE city = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (city, limit))
    history = cursor.fetchall()
    conn.close()
    return history