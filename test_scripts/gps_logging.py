import gpsd
import time
import datetime
import logging

# --- Configuration ---
LOG_FILE = "gps_log.txt"
LOG_INTERVAL_SECONDS = 5  # How often to log data (in seconds)

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_gps_data():
    try:
        # Connect to the local gpsd server
        gpsd.connect()
        logging.info("Connected to gpsd.")

        print(f"Logging GPS data to {LOG_FILE} every {LOG_INTERVAL_SECONDS} seconds. Press Ctrl+C to stop.")

        while True:
            # Get the current GPS position packet
            packet = gpsd.get_current()

            if packet.mode >= 2:  # 2D fix or 3D fix
                timestamp_utc = ""
                if packet.time:
                    try:
                        # Attempt to format the timestamp
                        timestamp_obj = datetime.datetime.strptime(packet.time, '%Y-%m-%dT%H:%M:%S.%fZ')
                        timestamp_utc = timestamp_obj.strftime('%Y-%m-%d %H:%M:%S UTC')
                    except ValueError:
                        timestamp_utc = packet.time # Fallback if parsing fails

                log_entry = (
                    f"Timestamp: {timestamp_utc}, "
                    f"Latitude: {packet.lat:.6f}, "
                    f"Longitude: {packet.lon:.6f}, "
                    f"Altitude: {packet.alt:.2f} m, "
                    f"Speed: {packet.hspeed:.2f} m/s, "
                    f"Climb: {packet.climb:.2f} m/s, "
                    f"Track: {packet.track:.2f} deg, "
                    f"Satellites: {packet.sats}, "
                  #  f"HDOP: {packet.hdop:.2f}, "
                  #  f"VDOP: {packet.vdop:.2f}, "
                  #  f"PDOP: {packet.pdop:.2f}, "
                    f"GPS Fix: {'3D' if packet.mode == 3 else '2D'}"
                )
                logging.info(log_entry)
                print(log_entry) # Also print to console for immediate feedback
            else:
                logging.warning("Waiting for GPS fix...")
                print("Waiting for GPS fix...")

            time.sleep(LOG_INTERVAL_SECONDS)

    except ConnectionRefusedError:
        logging.error("Could not connect to gpsd. Make sure gpsd is running: sudo gpsd /dev/ttyS0 -F /var/run/gpsd.sock")
        print("Error: Could not connect to gpsd. Make sure gpsd is running.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
    finally:
        logging.info("GPS logging stopped.")
        print("GPS logging stopped.")

if __name__ == "__main__":
    log_gps_data()
