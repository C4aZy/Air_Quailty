from flask import Flask, render_template, request, redirect, url_for
import folium
import requests
from database import init_db, add_report, get_all_reports, save_air_quality, get_air_quality_history
import os

app = Flask(__name__)

# Your API token from aqicn.org
API_TOKEN = 'b1f9ed8e519bb4bea12fbf00388e1a95481d2550'  # Replace with your actual token

# Initialize database
if not os.path.exists('data'):
    os.makedirs('data')
init_db()

def get_aqi_color(aqi):
    """Return color based on AQI level"""
    if aqi <= 50:
        return 'green'
    elif aqi <= 100:
        return 'yellow'
    elif aqi <= 150:
        return 'orange'
    elif aqi <= 200:
        return 'red'
    elif aqi <= 300:
        return 'purple'
    else:
        return 'maroon'

def get_aqi_category(aqi):
    """Return health category based on AQI"""
    if aqi <= 50:
        return 'Good'
    elif aqi <= 100:
        return 'Moderate'
    elif aqi <= 150:
        return 'Unhealthy for Sensitive Groups'
    elif aqi <= 200:
        return 'Unhealthy'
    elif aqi <= 300:
        return 'Very Unhealthy'
    else:
        return 'Hazardous'

def fetch_air_quality(city):
    """Fetch air quality data from AQICN API"""
    try:
        url = f"https://api.waqi.info/feed/{city}/?token={API_TOKEN}"
        response = requests.get(url)
        data = response.json()
        
        if data['status'] == 'ok':
            aqi = data['data']['aqi']
            pm25 = data['data']['iaqi'].get('pm25', {}).get('v', 0)
            lat = data['data']['city']['geo'][0]
            lon = data['data']['city']['geo'][1]
            
            # Save to database
            save_air_quality(city, aqi, pm25)
            
            return {
                'city': city,
                'aqi': aqi,
                'pm25': pm25,
                'lat': lat,
                'lon': lon,
                'category': get_aqi_category(aqi),
                'color': get_aqi_color(aqi)
            }
        else:
            return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

@app.route('/')
def index():
    # Default cities to monitor (you can change these)
    cities = ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata']
    
    # Create map centered on India
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
    
    air_data = []
    
    # Fetch and display air quality for each city
    for city in cities:
        data = fetch_air_quality(city)
        if data:
            air_data.append(data)
            
            # Add marker to map
            folium.CircleMarker(
                location=[data['lat'], data['lon']],
                radius=15,
                popup=f"{data['city']}<br>AQI: {data['aqi']}<br>{data['category']}",
                color=data['color'],
                fill=True,
                fillColor=data['color'],
                fillOpacity=0.7
            ).add_to(m)
    
    # Add community reports to map
    reports = get_all_reports()
    for report in reports:
        folium.Marker(
            location=[report[2], report[3]],
            popup=f"Community Report<br>{report[4]}<br>{report[5]}",
            icon=folium.Icon(color='red', icon='exclamation-sign')
        ).add_to(m)
    
    # Save map to HTML string
    map_html = m._repr_html_()
    
    return render_template('index.html', map_html=map_html, air_data=air_data)

@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        location = request.form['location']
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        pollution_type = request.form['pollution_type']
        description = request.form['description']
        
        add_report(location, latitude, longitude, pollution_type, description)
        
        return redirect(url_for('index'))
    
    return render_template('report.html')

@app.route('/statistics')
def statistics():
    # Get statistics for main cities
    cities = ['Delhi', 'Mumbai', 'Bangalore']
    stats = {}
    
    for city in cities:
        history = get_air_quality_history(city, limit=7)
        if history:
            avg_aqi = sum([h[0] for h in history]) / len(history)
            stats[city] = {
                'avg_aqi': round(avg_aqi, 1),
                'latest_aqi': history[0][0],
                'category': get_aqi_category(history[0][0]),
                'color': get_aqi_color(history[0][0])
            }
    
    reports = get_all_reports()
    
    return render_template('statistics.html', stats=stats, reports=reports)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)