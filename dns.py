import socket
import uselect
import uasyncio as asyncio


class DNSServer:
    def __init__(self, ip="192.168.4.1", port=53):
        self.ip = ip
        self.port = port

    async def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.sock.bind(("0.0.0.0", self.port))
        print("[DNS] Listening on port", self.port)

        poller = uselect.poll()
        poller.register(self.sock, uselect.POLLIN)

        while True:
            events = poller.poll(1000)  # timeout = 1000ms
            for sock, event in events:
                if event & uselect.POLLIN:
                    try:
                        data, addr = self.sock.recvfrom(512)
                        self.handle_request(data, addr)
                    except OSError as e:
                        print("recv error:", e)
            await asyncio.sleep(0)  # Yield control to event loop

    def handle_request(self, data, addr):
        if len(data) < 12:
            return

        dns_id = data[0:2]
        i = 12
        while data[i] != 0:
            i += 1 + data[i]
        query = data[12:i+5]

        response = dns_id
        response += b"\x81\x80"
        response += b"\x00\x01"
        response += b"\x00\x01"
        response += b"\x00\x00"
        response += b"\x00\x00"
        response += query

        response += b"\xc0\x0c"
        response += b"\x00\x01"
        response += b"\x00\x01"
        response += b"\x00\x00\x00\x3c"
        response += b"\x00\x04"
        response += bytes(map(int, self.ip.split('.')))

        try:
            self.sock.sendto(response, addr)
        except Exception as e:
            print("send error:", e)
