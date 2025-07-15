#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Filename: datalogger.py
Author: Ben Marosites
Email: marosite@email.sc.edu
Date: 2025-06-20
Version: 0.2
Description: This script collects temp, humidity, and GPS location data and writes that to a CSV file.
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
LOG_DIR = "/home/user/heat_project/log" # Define your log directory
LOG_INTERVAL_SECONDS = 5  # How often to log data (in seconds)

# --- Global Sensor Objects (initialized in main) ---
sht_sensor = None
# gps_connection = None # gpsd.connect() returns None, so no need for a global object here

# --- Setup Logging ---
# Ensure the log directory exists before setting up logging
os.makedirs(LOG_DIR, exist_ok=True)

# Generate a timestamped filename for the log file
current_datetime_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = os.path.join(LOG_DIR, f"sensor_log_{current_datetime_str}.csv")

# Configure logging
# Using logging.INFO for actual data, and logging.ERROR/WARNING for issues
# The 'level' parameter for basicConfig expects a logging level (e.g., logging.INFO), not 'print'
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO, # Changed from print to logging.INFO
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Also set up a console handler so you see logs in the terminal when running manually
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO) # Adjust as needed for console verbosity
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler) # Add the console handler to the root logger

logging.info(f"Logging sensor data to {LOG_FILE} every {LOG_INTERVAL_SECONDS} seconds.")
logging.info("Press Ctrl+C to stop.")

# --- Sensor Setup Functions ---

def setup_sht():
    """Initializes the SHT31D temperature/humidity sensor."""
    global sht_sensor # Declare that we're modifying the global sht_sensor object
    try:
        # Create the I2C bus
        i2c = busio.I2C(board.SCL, board.SDA)
        logging.info("I2C bus initialized successfully.")
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
    """Collects and logs sensor data continuously."""
    # Define CSV header
    csv_header = [
        "Timestamp_UTC", "Temperature_C", "Humidity_RH",
        "Latitude", "Longitude", "Altitude_m", "Speed_mps",
        "Climb_mps", "Track_deg", "Satellites", "GPS_Fix_Type"
    ]

    # Open CSV file and write header (only if file is new)
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        if not file_exists or os.stat(LOG_FILE).st_size == 0: # Check if file is empty or new
            csv_writer.writerow(csv_header)
            logging.info("CSV header written.")

        while True:
            current_log_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            
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
                temperature = "ERROR"
                humidity = "ERROR"

            # --- Read GPS Data ---
            packet = None
            try:
                # Get the current GPS position packet
                # This call can sometimes block if no data is coming, so a timeout might be useful
                packet = gpsd.get_current()
            except Exception as e:
                logging.error(f"Error getting GPS packet from gpsd: {e}")

            timestamp_gps_utc = "N/A"
            latitude = "N/A"
            longitude = "N/A"
            altitude = "N/A"
            speed = "N/A"
            climb = "N/A"
            track = "N/A"
            satellites = "N/A"
            gps_fix_type = "No Fix"

            if packet and packet.mode >= 2:  # 2D fix or 3D fix
                if packet.time:
                    try:
                        # Attempt to format the timestamp
                        timestamp_obj = datetime.datetime.strptime(packet.time, '%Y-%m-%dT%H:%M:%S.%fZ')
                        timestamp_gps_utc = timestamp_obj.strftime('%Y-%m-%d %H:%M:%S UTC')
                    except ValueError:
                        timestamp_gps_utc = packet.time # Fallback if parsing fails

                latitude = f'{packet.lat:.6f}'
                longitude = f'{packet.lon:.6f}'
                altitude = f'{packet.alt:.2f}' if hasattr(packet, 'alt') else "N/A" # 'alt' might not always be present
                speed = f'{packet.hspeed:.2f}' if hasattr(packet, 'hspeed') else "N/A"
                climb = f'{packet.climb:.2f}' if hasattr(packet, 'climb') else "N/A"
                track = f'{packet.track:.2f}' if hasattr(packet, 'track') else "N/A"
                satellites = packet.sats if hasattr(packet, 'sats') else "N/A"
                gps_fix_type = '3D' if packet.mode == 3 else '2D'
                logging.info(f"GPS Fix: {gps_fix_type}, Lat: {latitude}, Lon: {longitude}")
            else:
                logging.warning("Waiting for GPS fix or no GPS data available...")

            # --- Prepare Data Row ---
            data_row = [
                current_log_time, # Timestamp from Pi's system clock
                f"{temperature:.2f}" if isinstance(temperature, float) else temperature,
                f"{humidity:.2f}" if isinstance(humidity, float) else humidity,
                latitude, longitude, altitude, speed,
                climb, track, satellites, gps_fix_type
            ]

            # --- Write to CSV ---
            try:
                csv_writer.writerow(data_row)
                csvfile.flush() # Ensure data is written to disk immediately
                logging.info(f"Data logged: T={temperature}C, H={humidity}%, Lat={latitude}, Lon={longitude}")
            except Exception as e:
                logging.error(f"Error writing to CSV file: {e}")

            time.sleep(LOG_INTERVAL_SECONDS) # Wait for the next logging interval

# --- Main Execution Block ---

if __name__ == "__main__":
    try:
        setup_sht() # Initialize SHT31D sensor
        setup_gps() # Connect to gpsd
        log_data()  # Start the logging loop
    except KeyboardInterrupt:
        logging.info("Data logging stopped by user (Ctrl+C).")
    except Exception as e:
        logging.critical(f"A critical error occurred, stopping the datalogger: {e}", exc_info=True)
    finally:
        # Any cleanup code can go here, e.g., closing sensor connections if necessary
        # For SHT31D and gpsd, explicit close might not be strictly needed as
        # their underlying resources are often managed by the OS or the libraries.
        logging.info("Datalogger application finished.")
