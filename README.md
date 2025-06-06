# Transit Operations Dashboard

A real-time dashboard for transit operations teams to monitor and manage public transportation systems.

## Features

- Real-time vehicle tracking and status monitoring
- System-wide statistics and performance metrics
- Interactive map showing vehicle locations
- Real-time alerts and notifications
- Route performance analysis

## Prerequisites

- Python 3.8+
- PostgreSQL 17
- Node.js 14+
- npm 6+

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd OPERATIONALDASH
```

2. Set up the Python backend:
```bash
# Install Python dependencies
pip install -r requirements.txt
```

3. Load the GTFS data:
```bash
# Run the batch file to load data into PostgreSQL
load_data_final.bat
```

4. Set up the React frontend:
```bash
cd frontend
npm install
```

## Running the Application

1. Start the backend server:
```bash
# From the root directory
python main.py
```

2. Start the frontend development server:
```bash
# From the frontend directory
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Database Configuration

The application uses PostgreSQL with the following configuration:
- Host: localhost
- Port: 5432
- Database: GTFS
- Username: postgres
- Password: MODELING

## Data Loading Process

The application uses a batch file (`load_data_final.bat`) to load GTFS data into PostgreSQL. This process:
1. Cleans and validates the input data
2. Handles time format conversions (including times > 24:00:00)
3. Maintains referential integrity
4. Provides loading statistics

Required CSV files:
- agency.csv
- routes_cleaned_fixed.csv
- stops_clean.csv
- calendar.csv
- calendar_dates.csv
- trips_clean.csv
- stop_times_clean.csv

## Project Structure

```
OPERATIONALDASH/
├── frontend/                # React frontend application
├── db.py                   # Database configuration
├── models.py               # SQLAlchemy models
├── main.py                 # FastAPI backend server
├── load_data_final.bat     # Data loading batch file
├── load_gtfs_data_final.sql # SQL data loading script
└── requirements.txt        # Python dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 