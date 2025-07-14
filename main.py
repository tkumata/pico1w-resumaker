import network
import uasyncio as asyncio
from web import WebServer
from storage import Storage
import secrets
import display

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


async def main():
    # Display Wi-Fi info on OLED (assuming display.py handles this)
    ip = ap.ifconfig()[0]  # Get the IP address
    display.show_ap_info(ip)
    # Start web server
    await web_server.start()

# Run async main
asyncio.run(main())
