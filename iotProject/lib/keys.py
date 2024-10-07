import ubinascii              # Conversions between binary data and various encodings
import machine  

WIFI_SSID = 'xxx'
WIFI_PASS = 'xxx'

AIO_USER = "xxx"
AIO_KEY = "xxx"
AIO_SERVER = "io.adafruit.com"
AIO_PORT = 0000
AIO_CLIENT_ID = ubinascii.hexlify(machine.unique_id())

AIO_TEMP_FEED = "s17lduncan/feeds/temperature"
AIO_HUMID_FEED = "s17lduncan/feeds/humidity"

