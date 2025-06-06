from flask import Flask, render_template, jsonify
from flask_cors import CORS
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import random
import models
from db import SessionLocal
import json

app = Flask(__name__)
CORS(app)

# Load GTFS data from CSV files
try:
    routes_df = pd.read_csv('routes_clean.csv')
    stops_df = pd.read_csv('stops_clean.csv')
    trips_df = pd.read_csv('trips_clean.csv')
    stop_times_df = pd.read_csv('stop_times_clean.csv')
    calendar_df = pd.read_csv('calendar.csv')
    print("✅ GTFS CSV files loaded successfully")
except Exception as e:
    print(f"❌ Error loading CSV files: {e}")
    routes_df = stops_df = trips_df = stop_times_df = calendar_df = pd.DataFrame()

def get_db():
    try:
        db = SessionLocal()
        # Test the connection
        db.execute(text('SELECT 1'))
        return db
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def simulate_current_time():
    """Simulate current operational time (always during service hours)"""
    now = datetime.now()
    # Simulate time during peak hours for more interesting data
    service_hour = random.choice([7, 8, 9, 16, 17, 18])  # Peak hours
    return now.replace(hour=service_hour, minute=random.randint(0, 59))

def get_active_trips():
    """Get currently active trips based on real GTFS data"""
    current_time = simulate_current_time()
    current_time_str = current_time.strftime('%H:%M:%S')
    
    if stop_times_df.empty or trips_df.empty:
        return []
    
    # Get trips that should be active at current time
    active_stop_times = stop_times_df[
        (stop_times_df['departure_time'] <= current_time_str) & 
        (stop_times_df['arrival_time'] >= (current_time - timedelta(hours=1)).strftime('%H:%M:%S'))
    ].head(25)  # Limit for performance
    
    active_trips = []
    for _, stop_time in active_stop_times.iterrows():
        trip_info = trips_df[trips_df['trip_id'] == stop_time['trip_id']]
        if not trip_info.empty:
            trip = trip_info.iloc[0]
            route_info = routes_df[routes_df['route_id'] == trip['route_id']]
            stop_info = stops_df[stops_df['stop_id'] == stop_time['stop_id']]
            
            if not route_info.empty and not stop_info.empty:
                route = route_info.iloc[0]
                stop = stop_info.iloc[0]
                
                # Simulate real-time delays and positions
                delay_minutes = np.random.choice([0, 0, 0, 1, 2, 3, 5, 8], p=[0.4, 0.2, 0.1, 0.1, 0.1, 0.05, 0.03, 0.02])
                status = "Pünktlich" if delay_minutes <= 2 else "Verspätet" if delay_minutes <= 5 else "Stark verspätet"
                
                # Use real stop coordinates with slight variation for vehicle position
                base_lat = float(stop['stop_lat']) if pd.notna(stop['stop_lat']) else 48.2082
                base_lon = float(stop['stop_lon']) if pd.notna(stop['stop_lon']) else 16.3738
                
                active_trips.append({
                    'trip_id': str(trip['trip_id']),
                    'route_id': str(route['route_id']),
                    'route_name': str(route['route_short_name']),
                    'route_long_name': str(route.get('route_long_name', route['route_short_name'])),
                    'vehicle_id': f"WL-{random.randint(1000, 9999)}",
                    'status': status,
                    'delay_minutes': int(delay_minutes),
                    'current_stop': str(stop['stop_name']),
                    'stop_id': str(stop['stop_id']),
                    'passengers': random.randint(5, 80),
                    'capacity': 100,
                    'lat': float(base_lat + random.uniform(-0.001, 0.001)),
                    'lng': float(base_lon + random.uniform(-0.001, 0.001)),
                    'speed': random.randint(15, 45),  # km/h
                    'next_stop_eta': random.randint(1, 8),  # minutes
                    'last_update': current_time.strftime('%H:%M:%S')
                })
    
    return active_trips[:20]  # Return top 20 for display

def get_system_overview():
    """Get real-time system overview"""
    db = get_db()
    
    # Try database first, fall back to CSV
    if db is not None:
        try:
            total_routes = db.query(func.count(models.Route.route_id)).scalar()
            total_stops = db.query(func.count(models.Stop.stop_id)).scalar()
            total_trips = db.query(func.count(models.Trip.trip_id)).scalar()
            data_source = "Database"
            print(f"✅ Using DATABASE: {total_routes} routes, {total_stops} stops, {total_trips} trips")
            db.close()
        except Exception as e:
            print(f"⚠️  Database query error, using CSV: {e}")
            if db:
                db.close()
            db = None
    
    if db is None:
        total_routes = len(routes_df) if not routes_df.empty else 0
        total_stops = len(stops_df) if not stops_df.empty else 0
        total_trips = len(trips_df) if not trips_df.empty else 0
        data_source = "CSV Files"
        print(f"📊 Using CSV: {total_routes} routes, {total_stops} stops, {total_trips} trips")
    
    active_vehicles = len(get_active_trips())
    operational_routes = min(total_routes, active_vehicles) if total_routes > 0 else 0
    
    return {
        'total_routes': int(total_routes),
        'total_stops': int(total_stops),
        'active_vehicles': int(active_vehicles),
        'operational_routes': int(operational_routes),
        'system_status': 'Operativ' if active_vehicles > 0 else 'Eingeschränkt',
        'data_source': data_source,
        'last_update': datetime.now().strftime('%H:%M:%S')
    }

def get_route_status():
    """Get current status of all routes"""
    if routes_df.empty:
        return []
    
    route_status = []
    for _, route in routes_df.head(15).iterrows():  # Limit for performance
        # Simulate route operational status
        vehicles_on_route = random.randint(1, 8)
        avg_delay = random.uniform(0, 12)
        on_time_perf = max(60, 100 - (avg_delay * 5))
        
        status = "Normal"
        if avg_delay > 8:
            status = "Störung"
        elif avg_delay > 5:
            status = "Verspätung"
        
        route_status.append({
            'route_id': str(route['route_id']),
            'route_name': str(route['route_short_name']),
            'route_long_name': str(route.get('route_long_name', route['route_short_name'])),
            'vehicles_active': int(vehicles_on_route),
            'avg_delay': float(round(avg_delay, 1)),
            'on_time_performance': float(round(on_time_perf, 1)),
            'status': status,
            'passengers_total': random.randint(50, 400),
            'alerts_count': random.randint(0, 3)
        })
    
    return route_status

def get_critical_alerts():
    """Get current critical operational alerts"""
    alert_types = [
        "Fahrzeugausfall auf Linie {route}",
        "Signalstörung bei Station {stop}",
        "Verspätung auf Linie {route} - {delay} Min",
        "Überfüllung bei Station {stop}",
        "Weichenstörung Bereich {area}",
        "Witterungsbedingte Verzögerungen"
    ]
    
    alerts = []
    num_alerts = random.randint(2, 6)
    
    for i in range(num_alerts):
        alert_type = random.choice(alert_types)
        severity = random.choice(['Hoch', 'Mittel', 'Niedrig'])
        
        # Replace placeholders with real data
        if '{route}' in alert_type and not routes_df.empty:
            route = routes_df.sample(1).iloc[0]
            alert_type = alert_type.replace('{route}', route['route_short_name'])
        
        if '{stop}' in alert_type and not stops_df.empty:
            stop = stops_df.sample(1).iloc[0]
            alert_type = alert_type.replace('{stop}', stop['stop_name'])
        
        if '{delay}' in alert_type:
            delay = random.randint(5, 20)
            alert_type = alert_type.replace('{delay}', str(delay))
        
        if '{area}' in alert_type:
            areas = ['Zentrum', 'Süden', 'Norden', 'Osten', 'Westen']
            alert_type = alert_type.replace('{area}', random.choice(areas))
        
        alerts.append({
            'id': i + 1,
            'message': alert_type,
            'severity': severity,
            'timestamp': (datetime.now() - timedelta(minutes=random.randint(1, 120))).strftime('%H:%M'),
            'acknowledged': random.choice([True, False])
        })
    
    return alerts

def get_passenger_flow():
    """Get current passenger flow data"""
    if stops_df.empty:
        return {'hourly_data': [], 'station_loads': []}
    
    # Generate hourly passenger data for today
    hourly_data = []
    current_hour = datetime.now().hour
    
    for hour in range(24):
        # Simulate realistic passenger patterns
        if 6 <= hour <= 9:  # Morning rush
            base_load = 800 + random.randint(-100, 200)
        elif 16 <= hour <= 19:  # Evening rush
            base_load = 750 + random.randint(-100, 200)
        elif 10 <= hour <= 15:  # Midday
            base_load = 400 + random.randint(-50, 100)
        elif 20 <= hour <= 23:  # Evening
            base_load = 300 + random.randint(-50, 100)
        else:  # Night/early morning
            base_load = 50 + random.randint(-20, 50)
        
        hourly_data.append({
            'hour': f"{hour:02d}:00",
            'passengers': max(0, base_load),
            'is_current': hour == current_hour
        })
    
    # Top stations by current load
    station_loads = []
    for _, stop in stops_df.sample(min(10, len(stops_df))).iterrows():
        current_load = random.randint(5, 150)
        capacity = 200
        
        station_loads.append({
            'stop_name': str(stop['stop_name']),
            'current_load': int(current_load),
            'capacity': int(capacity),
            'load_percentage': float(round((current_load / capacity) * 100, 1)),
            'waiting_time': random.randint(1, 8)
        })
    
    return {
        'hourly_data': hourly_data,
        'station_loads': sorted(station_loads, key=lambda x: x['load_percentage'], reverse=True)
    }

# API Routes
@app.route('/')
def operational_dashboard():
    return render_template('operational_dashboard.html')

@app.route('/api/system-overview')
def api_system_overview():
    return jsonify(get_system_overview())

@app.route('/api/active-trips')
def api_active_trips():
    return jsonify(get_active_trips())

@app.route('/api/route-status')
def api_route_status():
    return jsonify(get_route_status())

@app.route('/api/critical-alerts')
def api_critical_alerts():
    return jsonify(get_critical_alerts())

@app.route('/api/passenger-flow')
def api_passenger_flow():
    return jsonify(get_passenger_flow())

@app.route('/api/system-health')
def api_system_health():
    """Real-time system health metrics"""
    # Test database connectivity
    db = get_db()
    db_status = "Connected" if db is not None else "Disconnected"
    if db:
        db.close()
    
    return jsonify({
        'overall_health': random.randint(85, 98),
        'network_status': 'Online',
        'database_status': db_status,
        'data_quality': random.randint(95, 100),
        'last_sync': datetime.now().strftime('%H:%M:%S'),
        'active_connections': random.randint(150, 300),
        'system_load': random.randint(25, 85)
    })

if __name__ == '__main__':
    print("🚇 Starting Wiener Linien Operational Dashboard...")
    print(f"📊 Loaded {len(routes_df)} routes, {len(stops_df)} stops, {len(trips_df)} trips")
    app.run(debug=True, host='0.0.0.0', port=5001) 