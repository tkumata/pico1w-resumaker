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

# QR コードキャッシュと OLED 制御用の変数
qr_cache = None
display_on = True
display_cycle_running = False


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
    global qr_cache

    # QR コードをキャッシュから使用、または新規生成
    if qr_cache is None:
        qr = QRCode(version=3)
        qr.add_data(
            "WIFI:S:{};T:WPA;P:{};;URL:http://{}".format(ssid, passwd, ip), 0)
        matrix = qr.get_matrix()

        # QR コードマトリックスをキャッシュ
        qr_cache = {
            'matrix': matrix,
            'ip': ip
        }

        # QR モジュールを unload
        unload_modules()

    display.fill(COLORS["WHITE"])

    matrix = qr_cache['matrix']
    scale = 3

    for y in range(len(matrix)):  # type: ignore
        for x in range(len(matrix[0])):  # type: ignore
            if matrix[y][x]:  # type: ignore
                display.fill_rect(x * scale, y * scale,
                                  scale, scale, COLORS["BLACK"])
    display.text("IP: {}".format(
        qr_cache['ip']), 0, 120, COLORS["BLACK"], size=1)
    display.show()


def text(text, x, y, color, size=1):
    display.text(text, x, y, color, size=size)
    display.show()


def clear():
    display.fill(0)
    display.show()


def unload_modules():
    TARGET_MODULES = (
        # "lib.ssd1351",
        "lib.uQR",
        "litefont",
    )

    for name in dir(display):
        attr = getattr(display, name)
        modname = getattr(attr, "__module__", "")
        if modname in TARGET_MODULES:
            delattr(display, name)

    for mod in TARGET_MODULES:
        sys.modules.pop(mod, None)
    sys.modules.pop("framebuf", None)

    gc.collect()


def display_off_func():
    """OLED ディスプレイを OFF にする"""
    global display_on
    display.write_cmd(0xAE)  # SSD1351_CMD_DISPLAYOFF
    display_on = False


def display_on_func():
    """OLED ディスプレイを ON にする"""
    global display_on
    display.write_cmd(0xAF)  # SSD1351_CMD_DISPLAYON
    display_on = True


def show_cached_qr():
    """キャッシュされた QR コードを表示"""
    global qr_cache

    if qr_cache is None:
        return

    display.fill(COLORS["WHITE"])

    matrix = qr_cache['matrix']
    scale = 3

    for y in range(len(matrix)):  # type: ignore
        for x in range(len(matrix[0])):  # type: ignore
            if matrix[y][x]:  # type: ignore
                display.fill_rect(x * scale, y * scale,
                                  scale, scale, COLORS["BLACK"])
    display.text("IP: {}".format(
        qr_cache['ip']), 0, 120, COLORS["BLACK"], size=1)
    display.show()


async def start_display_cycle():
    """OLED ON/OFF サイクルを開始（120 秒 ON、1 秒 OFF）"""
    import uasyncio as asyncio
    global display_cycle_running
    display_cycle_running = True

    while display_cycle_running:
        if not display_on:
            display_on_func()
        show_cached_qr()

        # 表示維持
        for _ in range(1200):  # 120秒 = 1200 * 0.1秒
            if not display_cycle_running:
                return
            await asyncio.sleep_ms(100)

        display_off_func()

        # 非表示維持
        for _ in range(10):   # 1秒 = 10 * 0.1秒
            if not display_cycle_running:
                return
            await asyncio.sleep_ms(100)
