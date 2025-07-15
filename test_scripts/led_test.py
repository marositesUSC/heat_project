import RPi.GPIO as GPIO
import time

LED_SHT_PIN = 16
LED_GPS_STATUS_PIN = 20
LED_LOGGING_STATUS_PIN = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_SHT_PIN, GPIO.OUT)
GPIO.setup(LED_GPS_STATUS_PIN, GPIO.OUT)
GPIO.setup(LED_LOGGING_STATUS_PIN, GPIO.OUT)

try:
    while True:
        GPIO.output(LED_SHT_PIN, GPIO.HIGH)
        GPIO.output(LED_GPS_STATUS_PIN  , GPIO.HIGH)
        GPIO.output(LED_LOGGING_STATUS_PIN, GPIO.HIGH)
        time.sleep(1)

        GPIO.output(LED_SHT_PIN, GPIO.LOW)
        GPIO.output(LED_GPS_STATUS_PIN, GPIO.LOW)
        GPIO.output(LED_LOGGING_STATUS_PIN, GPIO.LOW)
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
