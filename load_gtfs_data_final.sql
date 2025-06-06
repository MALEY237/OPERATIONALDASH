-- GTFS Data Loading Script (Final Version with Cleaned Routes)
-- This script loads data from CSV files into the SQL Server database

-- Set database options
SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
SET ANSI_PADDING ON;
GO

-- Create function for GTFS time conversion
IF OBJECT_ID('dbo.convert_gtfs_time') IS NOT NULL
    DROP FUNCTION dbo.convert_gtfs_time;
GO

CREATE FUNCTION dbo.convert_gtfs_time(@time_str VARCHAR(10))
RETURNS TIME
AS
BEGIN
    DECLARE @result TIME;
    
    IF @time_str LIKE '[2-9][4-9]:%' OR @time_str LIKE '[3-9][0-9]:%'
        SET @result = DATEADD(HOUR, -24, CAST(@time_str AS TIME));
    ELSE
        SET @result = CAST(@time_str AS TIME);
    
    RETURN @result;
END;
GO

-- Drop existing tables
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'stop_times') DROP TABLE stop_times;
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'trips') DROP TABLE trips;
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'calendar_dates') DROP TABLE calendar_dates;
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'calendar') DROP TABLE calendar;
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'stops') DROP TABLE stops;
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'routes') DROP TABLE routes;
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'agency') DROP TABLE agency;

-- Create tables
CREATE TABLE agency (
    agency_id VARCHAR(255) PRIMARY KEY,
    agency_name VARCHAR(255),
    agency_url VARCHAR(255),
    agency_timezone VARCHAR(255),
    agency_lang VARCHAR(255),
    agency_fare_url VARCHAR(255)
);

CREATE TABLE routes (
    route_id VARCHAR(255) PRIMARY KEY,
    agency_id VARCHAR(255),
    route_short_name VARCHAR(255),
    route_long_name VARCHAR(255),
    route_type INT,
    route_color VARCHAR(255),
    route_text_color VARCHAR(255)
);

CREATE TABLE stops (
    stop_id VARCHAR(255) PRIMARY KEY,
    stop_name VARCHAR(255),
    stop_lat FLOAT,
    stop_lon FLOAT,
    zone_id VARCHAR(255)
);

CREATE TABLE calendar (
    service_id VARCHAR(255) PRIMARY KEY,
    monday BIT,
    tuesday BIT,
    wednesday BIT,
    thursday BIT,
    friday BIT,
    saturday BIT,
    sunday BIT,
    start_date DATE,
    end_date DATE
);

CREATE TABLE calendar_dates (
    service_id VARCHAR(255),
    date DATE,
    exception_type INT,
    PRIMARY KEY (service_id, date)
);

CREATE TABLE trips (
    trip_id VARCHAR(255) PRIMARY KEY,
    route_id VARCHAR(255),
    service_id VARCHAR(255),
    direction_id INT
);

CREATE TABLE stop_times (
    id INT IDENTITY(1,1) PRIMARY KEY,
    trip_id VARCHAR(255),
    arrival_time TIME,
    departure_time TIME,
    stop_id VARCHAR(255),
    stop_sequence INT
);

-- Create temporary tables for data loading
CREATE TABLE #temp_agency (
    agency_id VARCHAR(255),
    agency_name VARCHAR(255),
    agency_url VARCHAR(255),
    agency_timezone VARCHAR(255),
    agency_lang VARCHAR(255),
    agency_fare_url VARCHAR(255)
);

-- Load data using BULK INSERT
BULK INSERT #temp_agency
FROM 'agency.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    KEEPNULLS
);

-- Insert into agency with trimmed agency_id
INSERT INTO agency
SELECT 
    LTRIM(RTRIM(REPLACE(REPLACE(agency_id, '0', ' '), ' ', '0'))) as agency_id,
    agency_name,
    agency_url,
    agency_timezone,
    agency_lang,
    agency_fare_url
FROM #temp_agency;

-- Load Routes data
BULK INSERT routes
FROM 'routes_clean.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    KEEPNULLS
);

-- Load Stops data
BULK INSERT stops
FROM 'stops_clean.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    KEEPNULLS
);

-- Create temporary table for calendar
CREATE TABLE #temp_calendar (
    service_id VARCHAR(255),
    monday VARCHAR(10),
    tuesday VARCHAR(10),
    wednesday VARCHAR(10),
    thursday VARCHAR(10),
    friday VARCHAR(10),
    saturday VARCHAR(10),
    sunday VARCHAR(10),
    start_date VARCHAR(10),
    end_date VARCHAR(10)
);

BULK INSERT #temp_calendar
FROM 'calendar.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    KEEPNULLS
);

-- Insert into calendar with proper type conversion
INSERT INTO calendar
SELECT 
    service_id,
    CASE WHEN monday = '1' THEN 1 ELSE 0 END,
    CASE WHEN tuesday = '1' THEN 1 ELSE 0 END,
    CASE WHEN wednesday = '1' THEN 1 ELSE 0 END,
    CASE WHEN thursday = '1' THEN 1 ELSE 0 END,
    CASE WHEN friday = '1' THEN 1 ELSE 0 END,
    CASE WHEN saturday = '1' THEN 1 ELSE 0 END,
    CASE WHEN sunday = '1' THEN 1 ELSE 0 END,
    CONVERT(DATE, start_date, 112),
    CONVERT(DATE, end_date, 112)
FROM #temp_calendar;

-- Create temporary table for calendar_dates
CREATE TABLE #temp_calendar_dates (
    service_id VARCHAR(255),
    date VARCHAR(10),
    exception_type INT
);

BULK INSERT #temp_calendar_dates
FROM 'calendar_dates.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    KEEPNULLS
);

-- Insert into calendar_dates with proper date conversion
INSERT INTO calendar_dates
SELECT 
    service_id,
    CONVERT(DATE, date, 112),
    exception_type
FROM #temp_calendar_dates;

-- Create temporary table for trips
CREATE TABLE #temp_trips (
    trip_id VARCHAR(255),
    route_id VARCHAR(255),
    service_id VARCHAR(255),
    shape_id VARCHAR(255),
    trip_headsign VARCHAR(255),
    direction_id VARCHAR(255),
    block_id VARCHAR(255)
);

BULK INSERT #temp_trips
FROM 'trips_clean.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    KEEPNULLS
);

-- Create staging table for trips
CREATE TABLE #temp_trips_staging (
    trip_id VARCHAR(255),
    route_id VARCHAR(255),
    service_id VARCHAR(255),
    direction_id INT
);

-- Load the data into the staging table
INSERT INTO #temp_trips_staging
SELECT 
    trip_id,
    route_id,
    service_id,
    CASE 
        WHEN ISNUMERIC(direction_id) = 1 THEN CAST(direction_id AS INT)
        ELSE 0
    END as direction_id
FROM #temp_trips;

-- Insert into the final trips table
WITH RankedTrips AS (
    SELECT 
        t.trip_id,
        t.route_id,
        t.service_id,
        t.direction_id,
        ROW_NUMBER() OVER (PARTITION BY t.trip_id ORDER BY t.route_id) as rn
    FROM #temp_trips_staging t
    INNER JOIN routes r ON t.route_id = r.route_id
)
INSERT INTO trips (trip_id, route_id, service_id, direction_id)
SELECT trip_id, route_id, service_id, direction_id
FROM RankedTrips
WHERE rn = 1;

-- Clean up temporary tables
DROP TABLE #temp_agency;
DROP TABLE #temp_calendar;
DROP TABLE #temp_calendar_dates;
DROP TABLE #temp_trips;
DROP TABLE #temp_trips_staging;

-- Display summary statistics
SELECT 'Agency' as table_name, COUNT(*) as record_count FROM agency
UNION ALL
SELECT 'Routes', COUNT(*) FROM routes
UNION ALL
SELECT 'Stops', COUNT(*) FROM stops
UNION ALL
SELECT 'Calendar', COUNT(*) FROM calendar
UNION ALL
SELECT 'Calendar Dates', COUNT(*) FROM calendar_dates
UNION ALL
SELECT 'Trips', COUNT(*) FROM trips
UNION ALL
SELECT 'Stop Times', COUNT(*) FROM stop_times
ORDER BY table_name;

PRINT 'GTFS database created successfully!';
PRINT 'Ready for Operational Dashboard development!';

-- Create temporary table for stop_times
CREATE TABLE #temp_stop_times (
    trip_id VARCHAR(255),
    arrival_time VARCHAR(10),
    departure_time VARCHAR(10),
    stop_id VARCHAR(255),
    stop_sequence INT,
    pickup_type INT,
    drop_off_type INT,
    shape_dist_traveled DECIMAL(18,6)
);

BULK INSERT #temp_stop_times
FROM 'stop_times_clean.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    KEEPNULLS
);

-- Insert into stop_times with time conversion
INSERT INTO stop_times (trip_id, stop_sequence, stop_id, arrival_time, departure_time)
SELECT 
    tst.trip_id,
    tst.stop_sequence,
    tst.stop_id,
    dbo.convert_gtfs_time(tst.arrival_time),
    dbo.convert_gtfs_time(tst.departure_time)
FROM #temp_stop_times tst
INNER JOIN trips t ON tst.trip_id = t.trip_id
INNER JOIN stops s ON tst.stop_id = s.stop_id
WHERE tst.arrival_time IS NOT NULL 
    AND tst.departure_time IS NOT NULL
    AND tst.arrival_time != ''
    AND tst.departure_time != ''
    AND tst.arrival_time LIKE '__:__:__'
    AND tst.departure_time LIKE '__:__:__';

-- Add foreign key constraints
ALTER TABLE routes ADD CONSTRAINT routes_agency_id_fkey 
    FOREIGN KEY (agency_id) REFERENCES agency(agency_id);
ALTER TABLE trips ADD CONSTRAINT trips_route_id_fkey 
    FOREIGN KEY (route_id) REFERENCES routes(route_id);
ALTER TABLE stop_times ADD CONSTRAINT stop_times_trip_id_fkey 
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id);
ALTER TABLE stop_times ADD CONSTRAINT stop_times_stop_id_fkey 
    FOREIGN KEY (stop_id) REFERENCES stops(stop_id);

-- Clean up temporary tables
DROP TABLE #temp_stop_times;

-- Display summary statistics
SELECT 'Agency' as table_name, COUNT(*) as record_count FROM agency
UNION ALL
SELECT 'Routes', COUNT(*) FROM routes
UNION ALL
SELECT 'Stops', COUNT(*) FROM stops
UNION ALL
SELECT 'Calendar', COUNT(*) FROM calendar
UNION ALL
SELECT 'Calendar Dates', COUNT(*) FROM calendar_dates
UNION ALL
SELECT 'Trips', COUNT(*) FROM trips
UNION ALL
SELECT 'Stop Times', COUNT(*) FROM stop_times
ORDER BY table_name;

PRINT 'GTFS database created successfully!';
PRINT 'Ready for Operational Dashboard development!'; 