import display
import secrets

# from dns import DNSServer
from storage import Storage
from web import WebServer

import gc
import network
import sys
import uasyncio as asyncio


# Wi-Fi AP setup
ap = network.WLAN(network.AP_IF)
ap.config(essid=secrets.SSID, password=secrets.PASSWORD)
ap.active(True)

# Wi-Fi STA setup
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(secrets.STA_SSID, secrets.STA_PASSWORD)

# SPI and OLED setup (assuming display.py exists)
display.init_display()

# Initialize storage
storage = Storage()

# Initialize web server
web_server = WebServer(storage)

# Initialize dns server
# dns_server = DNSServer(ip=ap.ifconfig()[0])


def unload_modules():
    TARGET_MODULES = (
        "lib.ssd1351",
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


async def main():
    ip = ap.ifconfig()[0]
    # display.show_ap_info(ip)

    # Show QR code with Wi-Fi credentials
    display.show_qr_code(ip, secrets.SSID, secrets.PASSWORD)

    # check memory
    # print("Before Memory Free:", gc.mem_free() / 1024, "KB")

    # unload unnecessary modules
    unload_modules()

    # check memory
    # print("After Memory Free:", gc.mem_free() / 1024, "KB")

    # start servers
    await asyncio.gather(
        web_server.start(),
        # dns_server.start(),
    )

# Run async main
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
    except Exception as e:
        print("Fatal error:", e)
    finally:
        ap.active(False)
        sta.active(False)
