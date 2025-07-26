import uasyncio as asyncio
import ujson
import os
import display
import gc


class WebServer:
    def __init__(self, storage):
        self.upload_headers = {}
        self.storage = storage
        self.routes = {
            "/": self.handle_index,
            "/hotspot-detect.html": self.handle_hotspot_detect,
            "/admin/user": self.handle_user,
            "/admin/simplehist": self.handle_simplehist,
            "/admin/jobhist": self.handle_jobhist,
            "/admin/portrait": self.handle_portrait,
            "/api/user": self.handle_api_user,
            "/api/simplehist": self.handle_api_simplehist,
            "/api/jobhist": self.handle_api_jobhist,
            "/api/portrait": self.handle_api_portrait,
            "/api/upload": self.handle_image_upload,
        }

    async def start(self):
        _ = await asyncio.start_server(self.handle_client, "0.0.0.0", 80)
        display.text("■", 0, 0, 0x07E0, size=1)
        while True:
            await asyncio.sleep(1)

    async def handle_client(self, reader, writer):
        try:
            gc.collect()
            headers = await self.parse_headers(reader)
            if not headers:
                return await self.send_error(writer, "400 Bad Request", "Null Request")

            method, path = self.parse_request_line(headers[0])
            if not method:
                return await self.send_error(writer, "400 Bad Request", "Bad Request Line")

            content_length = self.get_content_length(headers[1:])
            body = None

            if method == "POST" and content_length > 0:
                body_bytes = await self.read_exact(reader, content_length)
                if path == "/api/upload":
                    self.upload_headers = self.extract_custom_headers(
                        headers[1:])
                    body = body_bytes
                else:
                    try:
                        body = ujson.loads(body_bytes.decode("utf-8"))
                    except (UnicodeError, ValueError):
                        return await self.send_error(writer, "400 Bad Request", "JSON Decode Error")

            if method == "GET" and path in self.routes and path.startswith("/admin"):
                return await self.serve_admin_static(writer, path)
            elif method == "GET" and path in ("/api/jobhist", "/api/portrait"):
                return await self.serve_csv_as_json(writer, path)
            elif path in self.routes:
                handler = self.routes[path]
                content_type = "application/json" if path.startswith(
                    "/api/") else "text/html"
                await self.send_response_header(writer, "200 OK", content_type)
                await handler(method, body, writer)
            else:
                return await self.serve_static_file(writer, path)

        except MemoryError as e:
            print("handle_client memory error:", e)
        except Exception as e:
            print("handle_client error:", e)
        finally:
            if writer:
                try:
                    await writer.wait_closed()
                except Exception as e:
                    print("Error closing writer:", e)

    async def parse_headers(self, reader):
        headers = []
        while True:
            line = await reader.readline()
            if not line or line == b"\r\n":
                break
            try:
                headers.append(line.decode("utf-8").strip())
            except UnicodeError:
                return None
        return headers

    def parse_request_line(self, line):
        try:
            method, path, _ = line.split()
            return method, path
        except ValueError:
            return None, None

    def get_content_length(self, headers):
        for header in headers:
            if header.lower().startswith("content-length:"):
                try:
                    return int(header.split(":", 1)[1].strip())
                except ValueError:
                    return 0
        return 0

    async def read_exact(self, reader, total_length):
        buf = b""
        while len(buf) < total_length:
            chunk = await reader.read(total_length - len(buf))
            if not chunk:
                break
            buf += chunk
        return buf

    def extract_custom_headers(self, headers):
        result = {}
        for header in headers:
            if ":" in header:
                key, value = header.split(":", 1)
                result[key.strip().lower()] = value.strip()
        return result

    async def send_response_header(self, writer, status, content_type):
        header = (
            f"HTTP/1.1 {status}\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Connection: close\r\n\r\n"
        ).encode()
        writer.write(header)
        await writer.drain()

    async def send_error(self, writer, status, message):
        response = ujson.dumps(
            {"status": "error", "message": message}).encode()
        await self.send_response_header(writer, status, "application/json")
        await self.send_chunked(writer, response)

    async def send_chunked(self, writer, data):
        chunk_size = 512
        for i in range(0, len(data), chunk_size):
            writer.write(data[i:i+chunk_size])
            await writer.drain()

    async def serve_static_file(self, writer, path):
        return await self._serve_file(writer, 'www' + path)

    async def serve_admin_static(self, writer, path):
        return await self._serve_file(writer, 'www' + path.replace("/admin", "") + ".html")

    async def _serve_file(self, writer, filepath):
        try:
            ext = filepath[filepath.rfind(
                '.'):].lower() if '.' in filepath else ''
            content_type = {
                ".css": "text/css",
                ".js": "application/javascript",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".html": "text/html"
            }.get(ext, "text/plain")

            await self.send_response_header(writer, "200 OK", content_type)

            mode = "rb" if ext in [".jpg", ".jpeg"] else "r"
            with open(filepath, mode) as file:
                while True:
                    chunk = file.read(512)
                    if not chunk:
                        break
                    writer.write(chunk if isinstance(chunk, bytes)
                                 else chunk.encode("utf-8"))
                    await writer.drain()
        except OSError:
            await self.send_error(writer, "404 Not Found", "Not Found")

    async def serve_csv_as_json(self, writer, path):
        filename = "data" + path.replace("/api", "") + ".csv"
        field_map = {
            "/api/jobhist": ["job_no", "job_name", "job_description"],
            "/api/portrait": ["portrait_no", "portrait_url", "portrait_summary"]
        }
        keys = field_map.get(path)
        if not keys:
            return await self.send_error(writer, "400 Bad Request", "Unknown API path")

        await self.send_response_header(writer, "200 OK", "application/json")
        writer.write(b'[\r\n')
        await writer.drain()

        with open(filename, "r") as f:
            first = True
            for line in f:
                if not first:
                    writer.write(b',')
                values = line.strip().split(",", len(keys) - 1)
                record = {k: (int(v) if k.endswith("_no") else v)
                          for k, v in zip(keys, values)}
                await self.send_chunked(writer, ujson.dumps(record).encode() + b'\r\n')
                first = False
        writer.write(b']\r\n\r\n')
        await writer.drain()

    async def stream_file(self, writer, path):
        try:
            with open(path, "r") as file:
                while True:
                    line = file.readline()
                    if not line:
                        break
                    writer.write(line.encode("utf-8"))
                    await writer.drain()
        except Exception as e:
            await self.send_error(writer, "500 Internal Server Error", str(e))

    async def handle_image_upload(self, method, data, writer=None):
        if method != "POST":
            return await self.send_chunked(
                writer,
                ujson.dumps(
                    {"status": "error", "message": "Method not allowed"}
                ).encode()
            )

        filename = self.upload_headers.get("x-filename", "tmp.jpg")
        is_final = self.upload_headers.get(
            "x-final", "false").lower() == "true"

        try:
            with open("/www/" + filename, "ab") as f:
                f.write(data)
        except Exception as e:
            return await self.send_chunked(
                writer,
                ujson.dumps(
                    {"status": "error", "message": "Write Error: " + str(e)}
                ).encode()
            )

        if is_final:
            try:
                os.rename("/www/tmp.jpg", "/www/image.jpg")
                return await self.send_chunked(
                    writer,
                    ujson.dumps(
                        {"status": "success", "message": "Upload complete"}
                    ).encode()
                )
            except OSError as e:
                return await self.send_chunked(
                    writer,
                    ujson.dumps(
                        {"status": "error",
                            "message": "Failure Rename: " + str(e)}
                    ).encode()
                )

        return await self.send_chunked(writer, ujson.dumps({"status": "success", "message": "Chunk received"}).encode())

    async def handle_index(self, method, data, writer):
        if not all((self.storage.read_user(), self.storage.read_simplehist(), self.storage.read_jobhist())):
            return await self.send_chunked(writer, b"Some csv are empty.")
        return await self.stream_file(writer, "www/index.html")

    async def handle_hotspot_detect(self, method, data, writer):
        return await self.stream_file(writer, "www/hotspot-detect.html")

    async def html_post_handler(self, method, data, filepath, write_func, writer):
        if method == "GET":
            return await self.stream_file(writer, filepath)
        if method == "POST":
            write_func(data)
            return await self.send_chunked(writer, ujson.dumps({"status": "success"}).encode())

    async def handle_user(self, method, data, writer):
        return await self.html_post_handler(method, data, "www/user.html", self.storage.write_user, writer)

    async def handle_simplehist(self, method, data, writer):
        return await self.html_post_handler(method, data, "www/simplehist.html", self.storage.write_simplehist, writer)

    async def handle_jobhist(self, method, data, writer):
        return await self.html_post_handler(method, data, "www/jobhist.html", self.storage.write_jobhist, writer)

    async def handle_portrait(self, method, data, writer):
        return await self.html_post_handler(method, data, "www/portrait.html", self.storage.write_portrait, writer)

    async def api_get_handler(self, method, read_func, writer):
        if method == "GET":
            return await self.send_chunked(writer, ujson.dumps(read_func()).encode())
        return await self.send_chunked(
            writer,
            ujson.dumps(
                {"status": "error", "message": "Method not allowed"}
            ).encode()
        )

    async def handle_api_user(self, method, data, writer):
        return await self.api_get_handler(method, self.storage.read_user, writer)

    async def handle_api_simplehist(self, method, data, writer):
        return await self.api_get_handler(method, self.storage.read_simplehist, writer)

    async def handle_api_jobhist(self, method, data, writer):
        return await self.api_get_handler(method, self.storage.read_jobhist, writer)

    async def handle_api_portrait(self, method, data, writer):
        return await self.api_get_handler(method, self.storage.read_portrait, writer)
