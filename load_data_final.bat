@echo off
echo Loading Vienna GTFS data into PostgreSQL database (Final Version with Cleaned Routes)...
set PGPASSWORD=MODELING
"C:\Program Files\PostgreSQL\17\bin\psql.exe" "host=localhost port=5432 dbname=GTFS user=postgres sslmode=prefer connect_timeout=10" -f load_gtfs_data_final.sql
echo.
echo Data loading complete!
pause 