import gc
import network
import uasyncio as asyncio
from web import WebServer
# from dns import DNSServer
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

# Initialize dns server
# dns_server = DNSServer(ip=ap.ifconfig()[0])


async def main():
    # Display Wi-Fi info on OLED (assuming display.py handles this)
    ip = ap.ifconfig()[0]  # Get the IP address
    # display.show_ap_info(ip)

    # Show QR code with Wi-Fi credentials
    display.show_qr_code(ip, secrets.SSID, secrets.PASSWORD)

    await asyncio.gather(
        # Start Web server
        web_server.start(),

        # Start DNS server
        # dns_server.start(),
    )

# Run async main
if __name__ == "__main__":
    try:
        gc.threshold(1024 * 8)
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
    except Exception as e:
        print("Fatal error:", e)
    finally:
        display.clear()
