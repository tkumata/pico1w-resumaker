import uasyncio as asyncio
import ujson
import os
import gc

# バッファサイズを定数として定義
BUFFER_SIZE = 1024
buffer_size = BUFFER_SIZE  # 後方互換性のため


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
        while True:
            await asyncio.sleep(1)

    async def handle_client(self, reader, writer):
        try:
            gc.collect()
            first_line, content_length, expect_continue, custom_headers = await self.parse_headers_optimized(reader)
            if not first_line:
                return await self.send_error(writer, "400 Bad Request", "Null Request")

            method, path = self.parse_request_line(first_line)
            if not method:
                return await self.send_error(writer, "400 Bad Request", "Bad Request Line")

            # Expect: 100-continue を確認し、レスポンスを返す
            if expect_continue:
                await self.send_continue(writer)

            body = None

            if method == "POST" and content_length > 0:
                if path == "/api/upload":
                    # Pass reader and length to handler for chunked processing
                    self.upload_headers = custom_headers
                    body = {"reader": reader, "content_length": content_length}
                else:
                    try:
                        success = await self.write_temp_file(reader, content_length)
                        if not success:
                            return await self.send_error(writer, "500 Internal Server Error", "File Write Error")
                        body = self.load_json_from_file()
                        if body is None:
                            return await self.send_error(writer, "400 Bad Request", "JSON Decode Error")
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

            del body

        except MemoryError as error:
            print("handle_client memory error:", error)
            try:
                await self.send_error(writer, "500 Internal Server Error", "Memory Error")
            except Exception:
                pass
        except OSError as error:
            print("handle_client I/O error:", error)
            try:
                await self.send_error(writer, "500 Internal Server Error", "File I/O Error")
            except Exception:
                pass
        except ValueError as error:
            print("handle_client value error:", error)
            try:
                await self.send_error(writer, "400 Bad Request", "Invalid Data")
            except Exception:
                pass
        except Exception as error:
            print("handle_client error:", error)
            try:
                await self.send_error(writer, "500 Internal Server Error", "Server Error")
            except Exception:
                pass
        finally:
            if writer:
                await self.safe_close(writer)
                del writer

    async def safe_close(self, writer):
        try:
            await writer.wait_closed()
        except Exception:
            pass

    async def send_continue(self, writer):
        writer.write(b"HTTP/1.1 100 Continue\r\n\r\n")
        await writer.drain()

    async def write_temp_file(self, reader, content_length, temp_path="temp.json"):
        try:
            with open(temp_path, "wb") as file_obj:
                remaining = content_length
                bufsize = buffer_size
                while remaining > 0:
                    chunk = await reader.read(min(bufsize, remaining))
                    if not chunk:
                        break
                    file_obj.write(chunk)
                    remaining -= len(chunk)
            return True
        except OSError as error:
            print("[write] Error:", error)
            return False

    def load_json_from_file(self, temp_path="temp.json"):
        try:
            with open(temp_path, "r") as file_obj:
                return ujson.load(file_obj)
        except Exception as error:
            print("Error parsing JSON file:", error)
            return None

    async def parse_headers_optimized(self, reader):
        first_line = None
        content_length = 0
        expect_continue = False
        custom_headers = {}

        while True:
            line = await reader.readline()
            if not line or line == b"\r\n":
                break
            try:
                line_str = line.decode("utf-8").strip()
                if first_line is None:
                    first_line = line_str
                elif line_str.lower().startswith("content-length:"):
                    content_length = int(line_str.split(":", 1)[1].strip())
                elif line_str.lower().startswith("expect: 100-continue"):
                    expect_continue = True
                elif line_str.lower().startswith(("x-filename:", "x-final:")):
                    key, value = line_str.split(":", 1)
                    custom_headers[key.strip().lower()] = value.strip()
            except (UnicodeError, ValueError):
                return None, 0, False, {}
        return first_line, content_length, expect_continue, custom_headers

    def parse_request_line(self, line):
        try:
            method, path, _ = line.split()
            return method, path
        except ValueError:
            return None, None

    async def send_response_header(self, writer, status, content_type):
        header = (
            f"HTTP/1.1 {status}\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Connection: close\r\n\r\n"
        ).encode()
        writer.write(header)
        await writer.drain()

    async def send_error(self, writer, status, message):
        await self.send_response_header(writer, status, "application/json")
        error_data = ujson.dumps({"status": "error", "message": message})
        await self.send_chunked(writer, error_data.encode())

    async def send_chunked(self, writer, data):
        chunk_size = buffer_size
        data_len = len(data)
        for i in range(0, data_len, chunk_size):
            end_pos = min(i + chunk_size, data_len)
            writer.write(data[i:end_pos])
            await writer.drain()

    async def serve_static_file(self, writer, path):
        return await self._serve_file(writer, 'www' + path)

    async def serve_admin_static(self, writer, path):
        return await self._serve_file(writer, 'www' + path.replace("/admin", "") + ".html")

    async def _serve_file(self, writer, filepath):
        try:
            # パストラバーサル対策: ".." を含むパスを拒否
            if ".." in filepath or not filepath.startswith("www"):
                return await self.send_error(writer, "403 Forbidden", "Access Denied")

            # ファイル拡張子を効率的に取得
            dot_pos = filepath.rfind('.')
            if dot_pos != -1:
                file_extension = filepath[dot_pos:].lower()
            else:
                file_extension = ''

            # 辞書をタプルのペアに変更してメモリ使用量を削減
            if file_extension == ".css":
                content_type = "text/css"
            elif file_extension == ".js":
                content_type = "application/javascript"
            elif file_extension in (".jpg", ".jpeg"):
                content_type = "image/jpeg"
            elif file_extension == ".html":
                content_type = "text/html"
            else:
                content_type = "text/plain"

            await self.send_response_header(writer, "200 OK", content_type)

            is_binary = file_extension in (".jpg", ".jpeg")
            mode = "rb" if is_binary else "r"
            with open(filepath, mode) as file_obj:
                while True:
                    chunk = file_obj.read(buffer_size)
                    if not chunk:
                        break
                    if is_binary:
                        writer.write(chunk)
                    else:
                        writer.write(chunk.encode("utf-8"))
                    await writer.drain()
        except OSError:
            await self.send_error(writer, "404 Not Found", "Not Found")

    async def serve_csv_as_json(self, writer, path):
        filename = "data" + path.replace("/api", "") + ".csv"
        field_map = {
            "/api/jobhist": ("job_no", "job_name", "job_description"),
            "/api/portrait": ("portrait_no", "portrait_url", "portrait_summary")
        }
        keys = field_map.get(path)
        if not keys:
            return await self.send_error(writer, "400 Bad Request", "Unknown API path")

        await self.send_response_header(writer, "200 OK", "application/json")
        writer.write(b'[\r\n')
        await writer.drain()

        try:
            with open(filename, "r") as file_obj:
                first = True
                while True:
                    line = file_obj.readline()
                    if not line:
                        break
                    line = line.strip()
                    if line:
                        if not first:
                            writer.write(b',')
                        values = line.split(",", len(keys) - 1)
                        record = {k: (int(v) if k.endswith("_no") else v)
                                  for k, v in zip(keys, values)}
                        await self.send_chunked(writer, ujson.dumps(record).encode() + b'\r\n')
                        first = False
                        del values, record
        except OSError:
            pass
        writer.write(b']\r\n\r\n')
        await writer.drain()

    async def stream_file(self, writer, path):
        try:
            with open(path, "r") as file_obj:
                while True:
                    line = file_obj.readline()
                    if not line:
                        break
                    writer.write(line.encode("utf-8"))
                    await writer.drain()
        except OSError:
            await self.send_error(writer, "500 Internal Server Error", "File read error")

    async def handle_image_upload(self, method, data, writer=None):
        if method != "POST":
            error_msg = ujson.dumps(
                {"status": "error", "message": "Method not allowed"})
            return await self.send_chunked(writer, error_msg.encode())

        filename = self.upload_headers.get("x-filename", "tmp.jpg")
        is_final = self.upload_headers.get(
            "x-final", "false").lower() == "true"
        
        # data is {"reader": reader, "content_length": content_length}
        reader = data.get("reader")
        content_length = data.get("content_length", 0)

        try:
            with open("/www/" + filename, "ab") as file_obj:
                remaining = content_length
                bufsize = buffer_size
                while remaining > 0:
                    chunk = await reader.read(min(bufsize, remaining))
                    if not chunk:
                        break
                    file_obj.write(chunk)
                    remaining -= len(chunk)
                    gc.collect()
        except Exception as error:
            error_msg = ujson.dumps(
                {"status": "error", "message": "Write Error: " + str(error)})
            return await self.send_chunked(writer, error_msg.encode())

        if is_final:
            try:
                # Remove existing file if it exists to ensure clean rename
                try:
                    os.remove("/www/image.jpg")
                except OSError:
                    pass
                    
                os.rename("/www/" + filename, "/www/image.jpg")
                success_msg = ujson.dumps(
                    {"status": "success", "message": "Upload complete"})
                return await self.send_chunked(writer, success_msg.encode())
            except OSError as error:
                error_msg = ujson.dumps(
                    {"status": "error", "message": "Failure Rename: " + str(error)})
                return await self.send_chunked(writer, error_msg.encode())

        success_msg = ujson.dumps(
            {"status": "success", "message": "Chunk received"})
        return await self.send_chunked(writer, success_msg.encode())

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
            success_msg = ujson.dumps({"status": "success"})
            return await self.send_chunked(writer, success_msg.encode())

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
            data = read_func()
            json_data = ujson.dumps(data)
            return await self.send_chunked(writer, json_data.encode())
        error_msg = ujson.dumps(
            {"status": "error", "message": "Method not allowed"})
        return await self.send_chunked(writer, error_msg.encode())

    async def handle_api_user(self, method, data, writer):
        return await self.api_get_handler(method, self.storage.read_user, writer)

    async def handle_api_simplehist(self, method, data, writer):
        return await self.api_get_handler(method, self.storage.read_simplehist, writer)

    async def handle_api_jobhist(self, method, data, writer):
        return await self.api_get_handler(method, self.storage.read_jobhist, writer)

    async def handle_api_portrait(self, method, data, writer):
        return await self.api_get_handler(method, self.storage.read_portrait, writer)
