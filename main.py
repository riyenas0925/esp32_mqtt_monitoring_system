# wifi config
wifi_ssid = "iPhone"
wifi_password = "testmqtt"


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


if __name__ == '__main__':
    main()
