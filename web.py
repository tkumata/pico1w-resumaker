import uasyncio as asyncio
import ujson


class WebServer:
    def __init__(self, storage):
        self.storage = storage
        self.routes = {
            "/": self.handle_index,
            "/admin/user": self.handle_user,
            "/admin/simplehist": self.handle_simplehist,
            "/admin/jobhist": self.handle_jobhist,
            "/api/user": self.handle_api_user,
            "/api/simplehist": self.handle_api_simplehist,
            "/api/jobhist": self.handle_api_jobhist
        }

    # バッファを実際の長さまで読み込むヘルパー関数
    async def read_exact(self, reader, total_length):
        buf = b""
        while len(buf) < total_length:
            chunk = await reader.read(total_length - len(buf))
            if not chunk:
                break
            buf += chunk
        return buf

    async def handle_client(self, reader, writer):
        try:
            request = (await reader.read(1024)).decode()
            request_lines = request.split("\n")

            try:
                method, path, _ = request_lines[0].split(" ")
            except ValueError:
                await self.send_error(
                    writer,
                    "400 Bad Request",
                    "Malformed request line"
                )
                return

            response = ""
            content_type = "text/html"
            status = "200 OK"

            if path in self.routes:
                if method == "GET":
                    response = await self.routes[path](method, None)
                    if path.startswith("/api/"):
                        content_type = "application/json"

                elif method == "POST":
                    content_length = 0
                    for line in request_lines:
                        if line.lower().startswith("content-length:"):
                            try:
                                content_length = int(
                                    line.split(":")[1].strip())
                            except ValueError:
                                await self.send_error(
                                    writer,
                                    "400 Bad Request",
                                    "Invalid Content-Length"
                                )
                                return

                    raw_body = await self.read_exact(reader, content_length)
                    try:
                        body = raw_body.decode("utf-8")
                    except UnicodeError as e:
                        print("Unicode decode error:", e)
                        print("raw_body:", raw_body)
                        await self.send_error(
                            writer,
                            "400 Bad Request",
                            "Invalid UTF-8"
                        )
                        return

                    try:
                        json_data = ujson.loads(body)
                    except ValueError as e:
                        print("JSON parse error:", e)
                        await self.send_error(
                            writer,
                            "400 Bad Request",
                            "Invalid JSON"
                        )
                        return

                    response = await self.routes[path](method, json_data)
                    content_type = "application/json"
            else:
                try:
                    with open(f"www{path}", "r") as f:
                        response = f.read()
                        if path.endswith(".css"):
                            content_type = "text/css"
                        elif path.endswith(".js"):
                            content_type = "application/javascript"
                except OSError:
                    status = "404 Not Found"
                    response = "Not Found"

            response_bytes = response.encode("utf-8")
            header = (
                f"HTTP/1.1 {status}\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(response_bytes)}\r\n"
                f"Connection: close\r\n"
                f"\r\n"
            ).encode("utf-8")
            writer.write(header + response_bytes)
            await writer.drain()

        except OSError as e:
            if e.args[0] == 104:  # ECONNRESET
                pass
            else:
                raise
        finally:
            writer.close()
            await writer.wait_closed()

    async def send_error(self, writer, status, message):
        response = ujson.dumps({"status": "error", "message": message})
        writer.write(
            (
                f"HTTP/1.1 {status}\r\n"
                f"Content-Type: application/json\r\n"
                f"\r\n"
                f"{response}"
            ).encode()
        )
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def handle_index(self, method, data):
        user = self.storage.read_user()
        simplehist = self.storage.read_simplehist()
        jobhist = self.storage.read_jobhist()
        if not (user and simplehist and jobhist):
            return "データなし"
        with open("www/index.html", "r") as f:
            html = f.read()
        return html

    async def handle_user(self, method, data):
        if method == "GET":
            with open("www/user.html", "r") as f:
                return f.read()
        elif method == "POST":
            self.storage.write_user(data)
            return ujson.dumps({"status": "success"})

    async def handle_simplehist(self, method, data):
        if method == "GET":
            with open("www/simplehist.html", "r") as f:
                return f.read()
        elif method == "POST":
            self.storage.write_simplehist(data)
            return ujson.dumps({"status": "success"})

    async def handle_jobhist(self, method, data):
        if method == "GET":
            with open("www/jobhist.html", "r") as f:
                return f.read()
        elif method == "POST":
            self.storage.write_jobhist(data)
            return ujson.dumps({"status": "success"})

    async def handle_api_user(self, method, data):
        if method == "GET":
            return ujson.dumps(self.storage.read_user())
        return ujson.dumps(
            {"status": "error", "message": "Method not allowed"}
        )

    async def handle_api_simplehist(self, method, data):
        if method == "GET":
            return ujson.dumps(self.storage.read_simplehist())
        return ujson.dumps(
            {"status": "error", "message": "Method not allowed"}
        )

    async def handle_api_jobhist(self, method, data):
        if method == "GET":
            return ujson.dumps(self.storage.read_jobhist())
        return ujson.dumps(
            {"status": "error", "message": "Method not allowed"}
        )

    async def start(self):
        _ = await asyncio.start_server(self.handle_client, "0.0.0.0", 80)
        while True:
            await asyncio.sleep(1)
