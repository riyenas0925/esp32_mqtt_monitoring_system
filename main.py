from time import sleep_ms
from machine import Pin


def main():
    led = Pin(16, Pin.OUT)

    while True:
        led.on()
        sleep_ms(500)
        led.off()
        sleep_ms(500)


if __name__ == '__main__':
    main()
