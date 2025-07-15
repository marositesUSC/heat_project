#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Filename: datalogger.py
Author: Ben Marosites
Email: marosite@email.sc.edu
Date: 2025-06-20 (Corrected: 2025-06-20, 21:32 EDT, Structure: 2025-06-20)
Version: 0.4
Description: This script collects temp, humidity, and GPS location data and writes that to a CSV file.
             It uses system's UTC time for primary timestamp and logs operational messages separately.
             Data is stored in a 'data' subfolder, operational logs in a 'logs' subfolder.
"""

# --- Imports ---
import os
import time
import datetime
import logging
import csv

# Sensor-specific imports (uncomment these once hardware is connected and libraries installed)
import board
import adafruit_sht31d
import busio
import gpsd

# --- Configuration ---
# Define the base directory for your project
# IMPORTANT: Adjust this path if your project is not in /home/user/heat_project
BASE_PROJECT_DIR = "/home/user/heat_project"

# Define subdirectories for logs and data
OPERATIONAL_LOGS_DIR = os.path.join(BASE_PROJECT_DIR, "logs")
CSV_DATA_DIR = os.path.join(BASE_PROJECT_DIR, "data")

LOG_INTERVAL_SECONDS = 5  # How often to log data (in seconds)

# --- Global Sensor Objects (initialized in main) ---
sht_sensor = None

# --- Setup Logging (for operational messages) ---
# Ensure the log directories exist before setting up logging or writing data
os.makedirs(OPERATIONAL_LOGS_DIR, exist_ok=True)
os.makedirs(CSV_DATA_DIR, exist_ok=True)

# Generate a timestamped filename for the *operational log file*
current_datetime_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OPERATIONAL_LOG_FILE = os.path.join(OPERATIONAL_LOGS_DIR, f"datalogger_operational_{current_datetime_str}.log")

logging.basicConfig(
    filename=OPERATIONAL_LOG_FILE, # This log is for script operations/errors, NOT data
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Also set up a console handler so you see logs in the terminal when running manually
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO) # Adjust as needed for console verbosity
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler) # Add the console handler to the root logger

logging.info(f"Datalogger starting. Operational logs to: {OPERATIONAL_LOG_FILE}")
logging.info(f"Data will be logged to CSV in: {CSV_DATA_DIR}")
logging.info(f"Logging interval: {LOG_INTERVAL_SECONDS} seconds.")
logging.info("Press Ctrl+C to stop.")

# --- Sensor Setup Functions ---

def setup_sht():
    """Initializes the SHT31D temperature/humidity sensor."""
    global sht_sensor # Declare that we're modifying the global sht_sensor object
    try:
        # Create the I2C bus
        i2c = busio.I2C(board.SCL, board.SDA)
        logging.info("I2C bus initialized successfully for SHT31D.")
    except Exception as e:
        logging.error(f"Error initializing I2C bus: {e}")
        logging.error("Please ensure I2C is enabled and wired correctly.")
        raise # Re-raise the exception to stop execution if I2C fails

    try:
        # Create the SHT31D sensor object
        sht_sensor = adafruit_sht31d.SHT31D(i2c)
        logging.info("SHT31D sensor object created.")
    except ValueError:
        logging.error("SHT31D not found at default address 0x44.")
        logging.error("Check wiring and run 'sudo i2cdetect -y 1'.")
        raise # Re-raise
    except Exception as e:
        logging.error(f"An unexpected error occurred while creating SHT31D sensor object: {e}")
        raise # Re-raise
    logging.info("-" * 30)


def setup_gps():
    """Connects to the local gpsd server."""
    try:
        gpsd.connect()
        logging.info("Connected to gpsd.")
    except ConnectionRefusedError:
        logging.error("Error: Could not connect to gpsd. Make sure gpsd is running.")
        logging.error("Try: sudo systemctl enable gpsd && sudo systemctl start gpsd")
        logging.error("Also check if a GPS device is connected and streaming data to gpsd.")
        raise # Re-raise
    except Exception as e:
        logging.error(f"An unexpected error occurred while connecting to gpsd: {e}")
        raise # Re-raise

# --- Main Data Logging Function ---

def log_data():
    """Collects and logs sensor data continuously to a CSV file."""

    # Generate a timestamped filename for the *CSV data file*
    csv_datetime_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    CSV_DATA_FILE = os.path.join(CSV_DATA_DIR, f"sensor_data_{csv_datetime_str}.csv")

    # Define CSV header
    csv_header = [
        "System_Timestamp_UTC", "Temperature_C", "Humidity_RH",
        "GPS_Timestamp_UTC", "Latitude", "Longitude", "Altitude_m", "Speed_mps",
        "Climb_mps", "Track_deg", "Satellites", "GPS_Fix_Type"
    ]

    # Open CSV file and write header (only if file is new)
    file_exists = os.path.exists(CSV_DATA_FILE)
    try:
        with open(CSV_DATA_FILE, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            if not file_exists or os.stat(CSV_DATA_FILE).st_size == 0: # Check if file is empty or new
                csv_writer.writerow(csv_header)
                logging.info(f"CSV header written to {CSV_DATA_FILE}")

            while True:
                # --- Get System UTC Timestamp ---
                # This is the timestamp of when the data was collected by the Pi
                system_timestamp_utc = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

                # --- Read SHT31D Data ---
                temperature = "N/A"
                humidity = "N/A"
                try:
                    if sht_sensor: # Check if sensor was initialized successfully
                        temperature = sht_sensor.temperature
                        humidity = sht_sensor.relative_humidity
                    else:
                        logging.warning("SHT31D sensor not initialized. Skipping temperature/humidity data.")
                except Exception as e:
                    logging.error(f"Error reading SHT31D sensor: {e}")
                    temperature = "READ_ERROR"
                    humidity = "READ_ERROR"

                # --- Read GPS Data ---
                packet = None
                try:
                    # Get the current GPS position packet
                    # This call can sometimes block if no data is coming, consider a timeout if needed
                    packet = gpsd.get_current()
                except Exception as e:
                    logging.error(f"Error getting GPS packet from gpsd: {e}")

                gps_timestamp_utc = "N/A"
                latitude = "N/A"
                longitude = "N/A"
                altitude = "N/A"
                speed = "N/A"
                climb = "N/A"
                track = "N/A"
                satellites = "N/A"
                gps_fix_type = "No Fix"

                if packet and packet.mode >= 2:  # 2D fix (mode 2) or 3D fix (mode 3)
                    if packet.time:
                        try:
                            # Attempt to format the GPS timestamp
                            gps_timestamp_obj = datetime.datetime.strptime(packet.time, '%Y-%m-%dT%H:%M:%S.%fZ')
                            gps_timestamp_utc = gps_timestamp_obj.strftime('%Y-%m-%d %H:%M:%S UTC')
                        except ValueError:
                            gps_timestamp_utc = packet.time # Fallback if parsing fails

                    latitude = f'{packet.lat:.6f}'
                    longitude = f'{packet.lon:.6f}'
                    altitude = f'{packet.alt:.2f}' if hasattr(packet, 'alt') else "N/A"
                    speed = f'{packet.hspeed:.2f}' if hasattr(packet, 'hspeed') else "N/A"
                    climb = f'{packet.climb:.2f}' if hasattr(packet, 'climb') else "N/A"
                    track = f'{packet.track:.2f}' if hasattr(packet, 'track') else "N/A"
                    satellites = packet.sats if hasattr(packet, 'sats') else "N/A"
                    gps_fix_type = '3D' if packet.mode == 3 else '2D'
                    logging.info(f"GPS Fix: {gps_fix_type}, Lat: {latitude}, Lon: {longitude}")
                else:
                    logging.warning("Waiting for GPS fix or no GPS data available from gpsd...")

                # --- Prepare Data Row for CSV ---
                data_row = [
                    system_timestamp_utc, # Primary timestamp from Pi's system clock (UTC)
                    f"{temperature:.2f}" if isinstance(temperature, float) else temperature,
                    f"{humidity:.2f}" if isinstance(humidity, float) else humidity,
                    gps_timestamp_utc,
                    latitude, longitude, altitude, speed,
                    climb, track, satellites, gps_fix_type
                ]

                # --- Write to CSV ---
                try:
                    csv_writer.writerow(data_row)
                    csvfile.flush() # Ensure data is written to disk immediately
                    os.fsync(csvfile.fileno()) # Force OS to write to physical disk
                    logging.info(f"Data logged to CSV: T={temperature}C, H={humidity}%, GPS_TS={gps_timestamp_utc}")
                except Exception as e:
                    logging.error(f"Error writing data row to CSV file: {e}")

                time.sleep(LOG_INTERVAL_SECONDS) # Wait for the next logging interval

    except ConnectionRefusedError:
        logging.critical("Could not connect to gpsd. Ensure gpsd is running and configured correctly.")
        # Re-raise to ensure the main error handler catches it and logs it as critical
        raise
    except Exception as e:
        logging.critical(f"An unhandled error occurred in log_data loop: {e}", exc_info=True)
        # Re-raise to ensure the main error handler catches it and logs it as critical
        raise
    finally:
        logging.info("Exiting log_data function.")


# --- Main Execution Block ---

if __name__ == "__main__":
    try:
        # Initialize sensors and services
        setup_sht()
        setup_gps()
        # Start the continuous data logging loop
        log_data()
    except KeyboardInterrupt:
        logging.info("Data logging stopped by user (Ctrl+C).")
    except Exception as e:
        # This catches any exceptions raised by setup functions or unhandled by log_data
        logging.critical(f"A critical error occurred, stopping the datalogger application: {e}", exc_info=True)
    finally:
        logging.info("Datalogger application finished.")
