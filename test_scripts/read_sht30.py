import board
import adafruit_sht31d
import busio
import time

print("Adafruit SHT30 Test")

# Create the I2C bus
# For Raspberry Pi, I2C bus 1 is typically used (GPIO2=SDA, GPIO3=SCL)
# The 'board' module abstracts this for you.
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    print("I2C bus initialized successfully.")
except Exception as e:
    print(f"Error initializing I2C bus: {e}")
    print("Please ensure I2C is enabled and wired correctly.")
    exit()

# Create the SHT31D sensor object
# The default I2C address for SHT30 is 0x44 (7-bit address)
try:
    sensor = adafruit_sht31d.SHT31D(i2c)
    print("SHT30 sensor object created.")
except ValueError:
    print("SHT30 not found at default address 0x44.")
    print("Check wiring and run 'sudo i2cdetect -y 1'.")
    exit()
except Exception as e:
    print(f"An unexpected error occurred while creating sensor object: {e}")
    exit()

print("-" * 30)

# Loop to read data
while True:
    try:
        temperature = sensor.temperature
        humidity = sensor.relative_humidity

        print(f"Temperature: {temperature:.2f} C / {temperature * 9/5 + 32:.2f} F")
        print(f"Humidity: {humidity:.2f} %")
        print("-" * 30)

    except Exception as e:
        print(f"Error reading sensor data: {e}")
        print("Trying again in 5 seconds...")

    time.sleep(5)
