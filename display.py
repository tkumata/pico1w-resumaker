from machine import Pin, SPI
from lib.ssd1351 import SSD1351
from lib.uQR import QRCode
import sys
import gc

import secrets

COLORS = {
    "BLACK": 0,
    "WHITE": 0xFFFF,
    "RED": 0xF800,
    "CYAN": 0x07FF,
}


class DisplayController:
    def __init__(self):
        self.spi = SPI(0, baudrate=10000000, polarity=0,
                       phase=0, sck=Pin(18), mosi=Pin(19))
        self.dc = Pin(16, Pin.OUT)
        self.cs = Pin(20, Pin.OUT)
        self.rst = Pin(17, Pin.OUT)

        self.display = SSD1351(128, 128, self.spi, self.dc, self.cs, self.rst)

        self.qr_cache = None
        self.is_on = True
        self.is_running = False

        self.init_display()

    def init_display(self):
        self.display.fill(0)
        self.display.show()

    def show_ap_info(self, ip):
        self.display.fill(0)
        self.display.text("==== Resume ====", 0, 0, COLORS["RED"], size=1)
        self.display.text("SSID:", 0, 16, 0xFFFF, size=1)
        self.display.text("{}".format(
            secrets.SSID), 0, 32, COLORS["CYAN"], size=2)
        self.display.text("PASS:", 0, 56, 0xFFFF, size=1)
        self.display.text(
            "{}".format(secrets.PASSWORD),
            0, 72, COLORS["CYAN"],
            size=2
        )
        self.display.text("IP:", 0, 96, 0xFFFF, size=1)
        self.display.text(ip, 0, 112, COLORS["CYAN"], size=1)
        self.display.show()

    def show_qr_code(self, ip, ssid, passwd):
        if self.qr_cache is None:
            qr = QRCode(version=3)
            qr.add_data(
                "WIFI:S:{};T:WPA;P:{};;URL:http://{}".format(ssid, passwd, ip), 0)
            matrix = qr.get_matrix()

            self.qr_cache = {
                'matrix': matrix,
                'ip': ip
            }

            self.unload_modules()

        self.show_cached_qr()

    def text(self, text, x, y, color, size=1):
        self.display.text(text, x, y, color, size=size)
        self.display.show()

    def clear(self):
        self.display.fill(0)
        self.display.show()

    def unload_modules(self):
        target_modules = (
            "lib.uQR",
            "litefont",
        )

        for name in dir(self.display):
            attr = getattr(self.display, name)
            modname = getattr(attr, "__module__", "")
            if modname in target_modules:
                delattr(self.display, name)

        for mod in target_modules:
            sys.modules.pop(mod, None)
        sys.modules.pop("framebuf", None)

        gc.collect()

    def display_off(self):
        self.display.write_cmd(0xAE)  # SSD1351_CMD_DISPLAYOFF
        self.is_on = False

    def display_on(self):
        self.display.write_cmd(0xAF)  # SSD1351_CMD_DISPLAYON
        self.is_on = True

    def show_cached_qr(self):
        if self.qr_cache is None:
            return

        self.display.fill(COLORS["WHITE"])

        matrix = self.qr_cache['matrix']
        scale = 3

        for y in range(len(matrix)):  # type: ignore
            for x in range(len(matrix[0])):  # type: ignore
                if matrix[y][x]:  # type: ignore
                    self.display.fill_rect(
                        x * scale, y * scale, scale, scale, COLORS["BLACK"])
        self.display.text("IP: {}".format(
            self.qr_cache['ip']), 0, 120, COLORS["BLACK"], size=1)
        self.display.show()

    async def start_display_cycle(self):
        import uasyncio as asyncio
        self.is_running = True

        while self.is_running:
            if not self.is_on:
                self.display_on()
            self.show_cached_qr()

            for _ in range(1200):
                if not self.is_running:
                    return
                await asyncio.sleep_ms(100)

            self.display_off()

            for _ in range(10):
                if not self.is_running:
                    return
                await asyncio.sleep_ms(100)

    def stop(self):
        self.is_running = False
