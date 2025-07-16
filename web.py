import uasyncio as asyncio
import ujson
import os


class WebServer:
    def __init__(self, storage):
        self.storage = storage
        self.routes = {
            "/": self.handle_index,
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
        while True:
            await asyncio.sleep(1)

    async def handle_client(self, reader, writer):
        try:
            headers = await self.parse_headers(reader)
            if headers is None:
                await self.send_error(
                    writer,
                    "400 Bad Request",
                    "空のリクエスト"
                )
                return

            method, path = self.parse_request_line(headers[0])
            if method is None:
                await self.send_error(
                    writer,
                    "400 Bad Request",
                    "リクエストラインが不正"
                )
                return

            content_length = self.get_content_length(headers[1:])
            body = None
            if method == "POST" and content_length > 0:
                body_bytes = await self.read_exact(reader, content_length)

                # Upload だけは JSON でなくバイナリとして処理
                if path == "/api/upload":
                    self.upload_headers = self.extract_custom_headers(
                        headers[1:])
                    body = body_bytes  # bytesのまま渡す
                else:
                    try:
                        body = ujson.loads(body_bytes.decode("utf-8"))
                    except (UnicodeError, ValueError):
                        await self.send_error(
                            writer,
                            "400 Bad Request",
                            "JSONデコードエラー"
                        )
                        return

            if path in self.routes:
                handler = self.routes[path]
                response = await handler(method, body)
                content_type = (
                    "application/json" if path.startswith("/api/")
                    else "text/html"
                )
                await self.send_response(
                    writer,
                    "200 OK",
                    response,
                    content_type
                )
            else:
                await self.serve_static_file(writer, path)

        except Exception as exc:
            print("handle_client error:", exc)
        finally:
            writer.close()
            await writer.wait_closed()

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
        return headers if headers else None

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
                    return int(header.split(":")[1].strip())
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
                result[key.strip()] = value.strip()
        return result

    async def send_response(self, writer, status, body, content_type):
        if isinstance(body, bytes):
            encoded = body
        else:
            encoded = body.encode() if isinstance(body, str) else body
        writer.write((
            f"HTTP/1.1 {status}\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(encoded)}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        ).encode())
        writer.write(encoded)
        await writer.drain()

    async def send_error(self, writer, status, message):
        response = ujson.dumps({
            "status": "error",
            "message": message
        })
        await self.send_response(
            writer,
            status,
            response,
            "application/json"
        )

    async def serve_static_file(self, writer, path):
        try:
            # バイナリファイルかどうかを判定
            is_binary = path.endswith(('.jpg', '.jpeg'))
            if is_binary:
                with open("www" + path, "rb") as file:
                    content = file.read()
            else:
                with open("www" + path, "r") as file:
                    content = file.read()
            content_type = "text/html"
            if path.endswith(".css"):
                content_type = "text/css"
            elif path.endswith(".js"):
                content_type = "application/javascript"
            elif path.endswith(".jpg"):
                content_type = "image/jpeg"
            await self.send_response(writer, "200 OK", content, content_type)
        except OSError:
            await self.send_error(writer, "404 Not Found", "Not Found")

    def read_file(self, path):
        with open(path, "r") as file:
            return file.read()

    # ----------------------
    # Handlers
    # ----------------------

    async def handle_image_upload(self, method, data):
        if method != "POST":
            return ujson.dumps({
                "status": "error",
                "message": "Method not allowed"
            })

        filename = self.upload_headers.get("X-Filename", "tmp.jpg")
        # is_final = self.upload_headers.get("X-Final", "false") == "true"
        content_length = int(self.upload_headers.get("Content-Length") or "0")

        try:
            with open("/www/" + filename, "ab") as f:
                f.write(data)
        except Exception as e:
            return ujson.dumps({
                "status": "error",
                "message": "書き込みエラー: " + str(e)
            })

        # todo: chunk の最後をちゃんと判定する
        if content_length < 1024:
            os.rename("/www/tmp.jpg", "/www/image.jpg")
            return ujson.dumps({
                "status": "success",
                "message": "Upload complete"
            })

        return ujson.dumps({
            "status": "success",
            "message": "Chunk received"
        })

    async def handle_index(self, method, data):
        if not all((
            self.storage.read_user(),
            self.storage.read_simplehist(),
            self.storage.read_jobhist()
        )):
            return "Some csv are empty."
        return self.read_file("www/index.html")

    async def handle_user(self, method, data):
        return await self.html_post_handler(
            method,
            data,
            "www/user.html",
            self.storage.write_user
        )

    async def handle_simplehist(self, method, data):
        return await self.html_post_handler(
            method,
            data,
            "www/simplehist.html",
            self.storage.write_simplehist
        )

    async def handle_jobhist(self, method, data):
        return await self.html_post_handler(
            method,
            data,
            "www/jobhist.html",
            self.storage.write_jobhist
        )

    async def handle_portrait(self, method, data):
        return await self.html_post_handler(
            method,
            data,
            "www/portrait.html",
            self.storage.write_portrait
        )

    async def html_post_handler(self, method, data, filepath, write_func):
        if method == "GET":
            return self.read_file(filepath)
        if method == "POST":
            write_func(data)
            return ujson.dumps({"status": "success"})

    async def handle_api_user(self, method, data):
        return await self.api_get_handler(method, self.storage.read_user)

    async def handle_api_simplehist(self, method, data):
        return await self.api_get_handler(method, self.storage.read_simplehist)

    async def handle_api_jobhist(self, method, data):
        return await self.api_get_handler(method, self.storage.read_jobhist)

    async def handle_api_portrait(self, method, data):
        return await self.api_get_handler(method, self.storage.read_portrait)

    async def api_get_handler(self, method, read_func):
        if method == "GET":
            return ujson.dumps(read_func())
        return ujson.dumps({
            "status": "error",
            "message": "Method not allowed"
        })
