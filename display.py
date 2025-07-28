import typing

from machine import Pin, SPI
from lib.ssd1351 import SSD1351
from lib.uQR import QRCode

import secrets

COLORS = {
    "BLACK": 0,
    "WHITE": 0xFFFF,
    "RED": 0xF800,
    "GREEN": 0x07E0,
    "BLUE": 0x001F,
    "YELLOW": 0xFFE0,
    "CYAN": 0x07FF,
    "MAGENTA": 0xF81F,
}

spi = SPI(0, baudrate=10000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19))
dc = Pin(16, Pin.OUT)
cs = Pin(20, Pin.OUT)
rst = Pin(17, Pin.OUT)

display = SSD1351(128, 128, spi, dc, cs, rst)


def init_display():
    display.fill(0)
    display.show()


def show_ap_info(ip):
    display.fill(0)
    display.text("==== Resume ====", 0, 0, COLORS["RED"], size=1)
    display.text("SSID:", 0, 16, 0xFFFF, size=1)
    display.text("{}".format(secrets.SSID), 0, 32, COLORS["CYAN"], size=2)
    display.text("PASS:", 0, 56, 0xFFFF, size=1)
    display.text(
        "{}".format(secrets.PASSWORD),
        0, 72, COLORS["CYAN"],
        size=2
    )
    display.text("IP:", 0, 96, 0xFFFF, size=1)
    display.text(ip, 0, 112, COLORS["CYAN"], size=1)
    display.show()


def show_qr_code(ip, ssid, passwd):
    display.fill(COLORS["WHITE"])

    qr = QRCode(version=3)
    qr.add_data(
        "WIFI:S:{};T:WPA;P:{};;URL:http://{}".format(ssid, passwd, ip), 0)

    matrix = qr.get_matrix()
    matrix = typing.cast(list[list[bool]], qr.get_matrix())

    scale = 3

    for y in range(len(matrix)):
        for x in range(len(matrix[0])):  # type: ignore
            if matrix[y][x]:
                display.fill_rect(x * scale, y * scale,
                                  scale, scale, COLORS["BLACK"])
    display.text("IP: {}".format(ip), 0, 120, COLORS["BLACK"], size=1)
    display.show()


def text(text, x, y, color, size=1):
    display.text(text, x, y, color, size=size)
    display.show()


def clear():
    display.fill(0)
    display.show()
