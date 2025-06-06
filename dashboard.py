from flask import Flask, render_template, jsonify
from flask_cors import CORS
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import models
from db import SessionLocal
import json

app = Flask(__name__)
CORS(app)

def get_db():
    db = SessionLocal()
    return db

def get_system_stats():
    """Get overall system statistics"""
    db = get_db()
    try:
        total_routes = db.query(func.count(models.Route.route_id)).scalar() or 0
        total_stops = db.query(func.count(models.Stop.stop_id)).scalar() or 0
        total_trips = db.query(func.count(models.Trip.trip_id)).scalar() or 0
        return {
            "total_routes": total_routes,
            "total_stops": total_stops,
            "total_trips": total_trips
        }
    except Exception as e:
        print(f"Error fetching system stats: {e}")
        return {"total_routes": 0, "total_stops": 0, "total_trips": 0}
    finally:
        db.close()

def get_active_vehicles():
    """Get active vehicles data"""
    db = get_db()
    try:
        trips = db.query(models.Trip).join(models.Route).limit(15).all()
        
        vehicles = []
        statuses = ["On Time", "Delayed", "Very Late"]
        for i, trip in enumerate(trips):
            vehicles.append({
                "trip_id": trip.trip_id,
                "route_name": trip.route.route_long_name or trip.route.route_short_name or f"Route {trip.route_id}",
                "status": statuses[i % 3],
                "current_stop": f"Stop {i+1}",
                "lat": 40.7128 + (i * 0.01),
                "lng": -74.0060 + (i * 0.01)
            })
        
        return vehicles
    except Exception as e:
        print(f"Error fetching active vehicles: {e}")
        return []
    finally:
        db.close()

def get_route_performance():
    """Get route performance data"""
    db = get_db()
    try:
        routes = db.query(models.Route).limit(10).all()
        performance_data = []
        
        for i, route in enumerate(routes):
            performance_data.append({
                "route_id": route.route_id,
                "route_name": route.route_long_name or route.route_short_name or f"Route {route.route_id}",
                "on_time_percentage": 95 - (i * 2),
                "total_trips": 20 + (i * 5),
                "avg_delay": i * 0.5
            })
        
        return performance_data
    except Exception as e:
        print(f"Error fetching route performance: {e}")
        return []
    finally:
        db.close()

# Routes
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/system-stats')
def api_system_stats():
    return jsonify(get_system_stats())

@app.route('/api/active-vehicles')
def api_active_vehicles():
    return jsonify(get_active_vehicles())

@app.route('/api/route-performance')
def api_route_performance():
    return jsonify(get_route_performance())

@app.route('/api/alerts')
def api_alerts():
    alerts = [
        {"id": 1, "level": "warning", "message": "Route 1: 5 min delay due to traffic", "timestamp": datetime.now().isoformat()},
        {"id": 2, "level": "info", "message": "Route 3: On schedule", "timestamp": datetime.now().isoformat()},
        {"id": 3, "level": "danger", "message": "Route 7: Vehicle breakdown reported", "timestamp": datetime.now().isoformat()}
    ]
    return jsonify(alerts)

@app.route('/api/passenger-stats')
def api_passenger_stats():
    # Generate 24 hours of sample data
    times = []
    counts = []
    now = datetime.now()
    
    for i in range(24):
        time_point = now - timedelta(hours=23-i)
        times.append(time_point.strftime('%H:%M'))
        counts.append(100 + i*10 + (i%3)*20)
    
    return jsonify({"times": times, "counts": counts})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 