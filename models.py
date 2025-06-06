from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Time, Boolean
from sqlalchemy.orm import relationship
from db import Base

class Agency(Base):
    __tablename__ = "agency"
    
    agency_id = Column(String, primary_key=True)
    agency_name = Column(String)
    agency_url = Column(String)
    agency_timezone = Column(String)
    agency_lang = Column(String)
    agency_fare_url = Column(String)
    
    routes = relationship("Route", back_populates="agency")

class Route(Base):
    __tablename__ = "routes"
    
    route_id = Column(String, primary_key=True)
    agency_id = Column(String, ForeignKey("agency.agency_id"))
    route_short_name = Column(String)
    route_long_name = Column(String)
    route_type = Column(Integer)
    route_color = Column(String)
    route_text_color = Column(String)
    
    agency = relationship("Agency", back_populates="routes")
    trips = relationship("Trip", back_populates="route")

class Trip(Base):
    __tablename__ = "trips"
    
    trip_id = Column(String, primary_key=True)
    route_id = Column(String, ForeignKey("routes.route_id"))
    service_id = Column(String)
    direction_id = Column(Integer)
    
    route = relationship("Route", back_populates="trips")
    stop_times = relationship("StopTime", back_populates="trip")

class Stop(Base):
    __tablename__ = "stops"
    
    stop_id = Column(String, primary_key=True)
    stop_name = Column(String)
    stop_lat = Column(Float)
    stop_lon = Column(Float)
    zone_id = Column(String)
    
    stop_times = relationship("StopTime", back_populates="stop")

class StopTime(Base):
    __tablename__ = "stop_times"
    
    id = Column(Integer, primary_key=True)
    trip_id = Column(String, ForeignKey("trips.trip_id"))
    arrival_time = Column(Time)
    departure_time = Column(Time)
    stop_id = Column(String, ForeignKey("stops.stop_id"))
    stop_sequence = Column(Integer)
    
    trip = relationship("Trip", back_populates="stop_times")
    stop = relationship("Stop", back_populates="stop_times")

class Calendar(Base):
    __tablename__ = "calendar"
    
    service_id = Column(String, primary_key=True)
    monday = Column(Boolean)
    tuesday = Column(Boolean)
    wednesday = Column(Boolean)
    thursday = Column(Boolean)
    friday = Column(Boolean)
    saturday = Column(Boolean)
    sunday = Column(Boolean)
    start_date = Column(Date)
    end_date = Column(Date)

class CalendarDate(Base):
    __tablename__ = "calendar_dates"
    
    service_id = Column(String, primary_key=True)
    date = Column(Date, primary_key=True)
    exception_type = Column(Integer)

class Shape(Base):
    __tablename__ = "shapes"
    
    shape_id = Column(String, primary_key=True)
    shape_pt_lat = Column(Float)
    shape_pt_lon = Column(Float)
    shape_pt_sequence = Column(Integer, primary_key=True) 