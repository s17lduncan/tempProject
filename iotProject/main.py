import machine
import micropython
from machine import Pin, SPI
import ssd1306
import time
import lib.wifiConnection as wifiConnection
import lib.keys as keys
from lib.mqtt import MQTTClient
import dht

#display and sensor setup

spi_port = 0
SCLK = 18
MOSI = 19  
CS = 16       
DC = 17
RST = 20

WIDTH = 128
HEIGHT = 64

tempSensor = dht.DHT11(machine.Pin(15))

spi = SPI(
    spi_port,
    baudrate=40000000,
    mosi=Pin(MOSI),
    sck=Pin(SCLK))

oled = ssd1306.SSD1306_SPI(WIDTH,HEIGHT,

    spi,
    dc=Pin(DC),
    res=Pin(RST),
    cs=Pin(CS),
    external_vcc=False
    )


def display(t, h):
    oled.fill(0)
    oled.text('CLIMATE', 15, 6, 1)
    Line()
    oled.text('Temp: ' + str(t), 15, 25, 1)
    oled.text('Humidity: ' + str(h), 15, 35, 1)
    oled.show()

def Line():
    lines = [i for i in range(15, 100)]

    for line in lines:
        oled.pixel(line, 18, 1)



TIME_INTERVAL = 20000    # milliseconds
last_sent_ticks = 0  # milliseconds
led = Pin("LED", Pin.OUT)   # led pin initialization for Raspberry Pi Pico W


# Callback Function to respond to messages from Adafruit IO
def sub_cb(topic, msg):          # sub_cb means "callback subroutine"
    print((topic, msg))          # Outputs the message that was received. Debugging use.
    if msg == b"ON":             # If message says "ON" ...
        led.on()                 # ... then LED on
    elif msg == b"OFF":          # If message says "OFF" ...
        led.off()                # ... then LED off
    else:                        # If any other message is received ...
        print("Unknown message") # ... do nothing but output that it happened.


# Function to publish random number to Adafruit IO MQTT server at fixed interval
def sendData():
    global last_sent_ticks
    global TIME_INTERVAL

    if ((time.ticks_ms() - last_sent_ticks) < TIME_INTERVAL):
        return; # Too soon since last one sent.
    
    try:
        tempSensor.measure()
    except Exception as error:
        print("Exception occurred", error)
        

    temp = tempSensor.temperature()
    humidity = tempSensor.humidity()
    
    display(temp, humidity)
    
    print("Publishing: Temperature: {0}  Humidity: {1} ... ".format(temp, humidity, keys.AIO_TEMP_FEED), end='')
    
    try:
        client.publish(topic=keys.AIO_TEMP_FEED, msg=str(temp))
        client.publish(topic=keys.AIO_HUMID_FEED, msg=str(humidity))
        print("DONE")
    except Exception as e:
        print("FAILED")
    finally:
        last_sent_ticks = time.ticks_ms()

# Try WiFi Connection
try:
    ip = wifiConnection.connect()
except KeyboardInterrupt:
    print("Keyboard interrupt")

# Use the MQTT protocol to connect to Adafruit IO
client = MQTTClient(keys.AIO_CLIENT_ID, keys.AIO_SERVER, keys.AIO_PORT, keys.AIO_USER, keys.AIO_KEY)

# Subscribed messages will be delivered to this callback
client.set_callback(sub_cb)
client.connect()
client.subscribe(keys.AIO_TEMP_FEED)
print("Connected to %s, subscribed to %s topic" % (keys.AIO_SERVER, keys.AIO_TEMP_FEED))



try:                      # Code between try: and finally: may cause an error
    while 1:              # Repeat this loop forever
        client.check_msg()# Action a message if one is received. Non-blocking.
        sendData()
        # Send a random number to Adafruit IO if it's time.
finally:                  # If an exception is thrown ...
    client.disconnect()   # ... disconnect the client and clean up.
    client = None
    wifiConnection.disconnect()
    print("Disconnected from Adafruit IO.")
