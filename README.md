# Transit Operations Dashboard

A real-time dashboard for transit operations teams to monitor and manage public transportation systems using Flask and GTFS data.

## Features

- **Real-time Vehicle Tracking**: Live monitoring of active vehicles with location and status
- **System Overview**: Comprehensive statistics including routes, stops, and active vehicles
- **Route Performance**: Real-time route status with delay information and on-time performance
- **Interactive Dashboard**: Web-based interface with live data updates
- **Critical Alerts**: System-wide alerts and notifications for operational issues
- **Passenger Flow Analytics**: Station load monitoring and hourly passenger patterns
- **System Health Monitoring**: Database connectivity and system performance metrics

## Prerequisites

- Python 3.8+
- PostgreSQL 17
- Flask web framework
- GTFS data files (CSV format)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd OPERATIONALDASH
```

2. Set up Python virtual environment (recommended):
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Unix/MacOS:
source .venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL database:
```bash
# Create database (run in PostgreSQL)
createdb GTFS
```

5. Load the GTFS data:
```bash
# Run the batch file to load data into PostgreSQL
load_data_final.bat
```

## Running the Application

Start the Flask server:
```bash
python operational_dashboard.py
```

The application will be available at:
- **Dashboard**: http://localhost:5001
- **API Documentation**: Available through various endpoints (see API section below)

## Database Configuration

The application uses PostgreSQL with the following configuration:
- **Host**: localhost
- **Port**: 5432
- **Database**: GTFS
- **Username**: postgres
- **Password**: MODELING

The application automatically falls back to CSV file data if database connection fails.

## Data Sources

### Required GTFS CSV Files:
- `agency.csv`
- `routes_clean.csv`
- `stops_clean.csv`
- `trips_clean.csv`
- `stop_times_clean.csv`
- `calendar.csv`
- `calendar_dates.csv`
- `shapes.csv`

### Data Loading Process:
The application uses a batch file (`load_data_final.bat`) to load GTFS data into PostgreSQL. This process:
1. Cleans and validates the input data
2. Handles time format conversions (including times > 24:00:00)
3. Maintains referential integrity
4. Provides loading statistics

## API Endpoints

The application provides RESTful API endpoints:

### Core Data
- `GET /api/system-overview` - System-wide statistics
- `GET /api/active-trips` - Currently active vehicles with real-time data
- `GET /api/routes` - Available routes for filtering
- `GET /api/route-status` - Performance metrics for all routes

### Operational Data
- `GET /api/critical-alerts` - Current system alerts and notifications
- `GET /api/passenger-flow` - Passenger flow analytics and station loads
- `GET /api/system-health` - System health and connectivity status

### Filtering
- `GET /api/active-trips?vehicle_type={type}` - Filter by vehicle type (U-Bahn, S-Bahn, Tram, Bus)
- `GET /api/active-trips?route={route}` - Filter by route name
- `GET /api/test-filter` - Debug endpoint for filter testing

## Project Structure

```
OPERATIONALDASH/
├── operational_dashboard.py    # Main Flask application
├── templates/
│   └── operational_dashboard.html  # Web interface template
├── models.py                   # SQLAlchemy database models
├── db.py                      # Database configuration
├── load_data_final.bat        # Data loading batch script
├── load_gtfs_data_final.sql    # SQL data loading script
├── requirements.txt           # Python dependencies
├── *.csv                      # GTFS data files
└── README.md                  # This file
```

## Application Features

### Dashboard Components
- **System Overview Panel**: Total routes, stops, active vehicles, and operational status
- **Active Vehicles Table**: Real-time vehicle tracking with status, delays, and passenger load
- **Route Status**: Performance metrics with on-time performance and delay information
- **Critical Alerts**: System-wide notifications and alerts
- **Passenger Flow**: Station load monitoring and hourly patterns

### Real-time Simulation
The application simulates real-time operational data including:
- Vehicle positions and movements
- Realistic delay patterns
- Passenger load simulation
- System alerts and notifications
- Time-based operational scenarios

## Development

### Running in Debug Mode
The application runs in debug mode by default for development:
```bash
python operational_dashboard.py
```

### Data Fallback Strategy
- Primary: PostgreSQL database
- Fallback: CSV files (if database unavailable)
- The application automatically detects and switches between data sources

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
