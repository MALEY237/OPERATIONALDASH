from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, time
from typing import List, Dict
import models
from db import SessionLocal, engine
import pandas as pd

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Transit Operations Dashboard")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Transit Operations Dashboard API"}

@app.get("/system-overview")
def get_system_overview(db: Session = Depends(get_db)):
    """Get overall system statistics"""
    try:
        total_routes = db.query(func.count(models.Route.route_id)).scalar()
        total_stops = db.query(func.count(models.Stop.stop_id)).scalar()
        total_trips = db.query(func.count(models.Trip.trip_id)).scalar()
        
        return {
            "total_routes": total_routes,
            "total_stops": total_stops,
            "total_trips": total_trips,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/active-vehicles")
def get_active_vehicles(db: Session = Depends(get_db)):
    """Get currently active vehicles and their status"""
    try:
        current_time = datetime.now().time()
        
        # Get all trips that are currently active
        active_trips = db.query(models.Trip)\
            .join(models.StopTime)\
            .join(models.Stop)\
            .join(models.Route)\
            .filter(
                and_(
                    models.StopTime.departure_time <= current_time,
                    models.StopTime.arrival_time >= current_time
                )
            ).all()
        
        return [{
            "trip_id": trip.trip_id,
            "route_name": trip.route.route_long_name,
            "status": "On Time",  # This would be calculated based on real-time data
            "current_stop": trip.stop_times[0].stop.stop_name,  # This would be updated with real-time data
            "current_location": {
                "lat": str(trip.stop_times[0].stop.stop_lat),  # Using first stop's location as placeholder
                "lng": str(trip.stop_times[0].stop.stop_lon)   # In real system, this would be real-time GPS data
            }
        } for trip in active_trips]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/route-performance/{route_id}")
def get_route_performance(route_id: str, db: Session = Depends(get_db)):
    """Get performance metrics for a specific route"""
    try:
        route = db.query(models.Route)\
            .filter(models.Route.route_id == route_id)\
            .first()
        
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        # Get all trips for this route
        trips = db.query(models.Trip)\
            .filter(models.Trip.route_id == route_id)\
            .all()
        
        return {
            "route_name": route.route_long_name,
            "total_trips": len(trips),
            "on_time_percentage": 95,  # This would be calculated from real-time data
            "average_delay": 3  # This would be calculated from real-time data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stops/{route_id}")
def get_route_stops(route_id: str, db: Session = Depends(get_db)):
    """Get all stops for a specific route"""
    try:
        stops = db.query(models.Stop)\
            .join(models.StopTime)\
            .join(models.Trip)\
            .filter(models.Trip.route_id == route_id)\
            .distinct()\
            .all()
        
        return [{
            "stop_id": stop.stop_id,
            "name": stop.stop_name,
            "latitude": stop.stop_lat,
            "longitude": stop.stop_lon
        } for stop in stops]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    """Get current system alerts"""
    # This would be connected to a real-time alert system
    return {
        "alerts": [
            {
                "id": 1,
                "type": "delay",
                "severity": "medium",
                "route_id": "route_1",
                "message": "10 minute delay due to traffic",
                "timestamp": datetime.now().isoformat()
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 