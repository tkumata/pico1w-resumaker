import network
import uasyncio as asyncio
from web import WebServer
# from dns import DNSServer
from storage import Storage
import secrets
import display
# import time

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
# dns_server = DNSServer(ip="192.168.4.1")


async def main():
    # Display Wi-Fi info on OLED (assuming display.py handles this)
    ip = ap.ifconfig()[0]  # Get the IP address
    # display.show_ap_info(ip)
    # time.sleep(3)
    display.show_qr_code(ip, secrets.SSID, secrets.PASSWORD)
    await asyncio.gather(
        # Start web server
        web_server.start(),
        # Start DNS server
        # dns_server.start()
    )

# Run async main
asyncio.run(main())
