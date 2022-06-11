from time import sleep, sleep_ms
from dht import DHT11
from machine import Pin, SoftI2C, freq
from umqtt.simple import MQTTClient
from neopixel import NeoPixel
from uos import uname
from usys import platform, implementation
from esp import flash_size

# Wi-Fi config
wifi_ssid = "iPhone"
wifi_password = "testmqtt"

# mqtt config
mqtt_server_host = "rabbitmq.riyenas.dev"
mqtt_client_id = "mqtt_client"
mqtt_topic = b"sensors/1"


def print_info():
    print("from uos.uname():")
    for u in uname():
        print(u)
    print()

    print("from usys:")
    print("usys.platform: ", platform)
    print("usys.implementation: ", implementation)
    print()

    print("====================================")
    print(implementation[0], uname()[3],
          "\nrun on", uname()[4])
    print("====================================")
    print("Flash size:", flash_size())
    print("CPU frequency:", freq(), "(Hz)")


def connect():
    import network

    station = network.WLAN(network.STA_IF)

    if station.isconnected():
        print("Already connected")
        return

    station.active(True)
    station.connect(wifi_ssid, wifi_password)

    while not station.isconnected():
        pass

    print("Connection successful")
    print(station.ifconfig())


def main():
    # connect Wi-Fi network
    connect()

    # print info
    print_info()

    # connect mqtt broker
    client = MQTTClient(mqtt_client_id, mqtt_server_host)
    client.connect()

    # init dht11 Temperature, Humidity sensor
    dht11 = DHT11(Pin(9))

    # init bh1750 Light Intensity Sensor
    bh1750_address = 0x23
    bh1750_power_off = 0x00
    bh1750_power_on = 0x01
    bh1750_reset = 0x07
    continuous_high_res_mode_2 = 0x11

    # init led
    np = NeoPixel(Pin(8), 1)

    # Soil Moisture Sensor Init
    soil_moisture_sensor = Pin(4, Pin.IN, Pin.PULL_DOWN)

    i2c = SoftI2C(scl=Pin(0), sda=Pin(1), freq=400000)

    # init bh1750
    i2c.writeto(bh1750_address, bytes([bh1750_power_off]))
    i2c.writeto(bh1750_address, bytes([bh1750_power_on]))
    i2c.writeto(bh1750_address, bytes([bh1750_reset]))
    i2c.writeto(bh1750_address, bytes([continuous_high_res_mode_2]))

    # publish message
    while True:
        try:
            # measure temp and humidity
            dht11.measure()
            humidity = dht11.humidity()
            temperature = dht11.temperature()

            # measure lux
            sleep_ms(120)
            data = i2c.readfrom(bh1750_address, 2)
            factor = 2.0
            lux = (data[0] << 8 | data[1]) / (1.2 * factor)

            # calc brightness
            weight = 325
            brightness = int(255 - lux * (255 / 65535 * weight))
            brightness = brightness if brightness >= 0 else 0
            np[0] = (brightness, brightness, brightness)
            np.write()

            # measure soil moisture
            soil_moisture = 1 if soil_moisture_sensor.value() else 0

            json = b'{"id": %u, "humidity": %.1f, "temperature": %.1f, "lux": %.1f, "brightness": %d, "isBarren": %d}' % (1, humidity, temperature, lux, brightness, soil_moisture)

            client.publish(mqtt_topic, json)
            print(mqtt_topic, json)

            sleep(30)

        except OSError as e:
            print("error: {0}".format(e))
            main()

    client.disconnect()


if __name__ == '__main__':
    main()
