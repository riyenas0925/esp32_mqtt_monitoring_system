from time import sleep
from umqtt.simple import MQTTClient

# Wi-Fi config
wifi_ssid = "iPhone"
wifi_password = "testmqtt"

# mqtt config
mqtt_server_host = "rabbitmq.riyenas.dev"
mqtt_client_id = "mqtt_client"
mqtt_topic = b"sensors/1"


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

    # connect mqtt broker
    client = MQTTClient(mqtt_client_id, mqtt_server_host)
    client.connect()

    # publish message
    while True:
        try:
            sleep(10)

            # dummy data
            humidity = 50.0
            temperature = 36.5
            lux = 1000

            json = b'{"id": %u, "humidity": %.1f, "temperature": %.1f, "lux": %.1f}' % (1, humidity, temperature, lux)

            client.publish(mqtt_topic, json)
            print(mqtt_topic, json)
        except OSError as e:
            print("error: {0}".format(e))

    client.disconnect()


if __name__ == '__main__':
    main()
