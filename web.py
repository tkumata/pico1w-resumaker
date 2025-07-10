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

    async def handle_client(self, reader, writer):
        try:
            request = (await reader.read(1024)).decode()
            request_lines = request.split("\n")
            method, path, _ = request_lines[0].split(" ")

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
                            content_length = int(line.split(":")[1].strip())
                    body = (await reader.read(content_length)).decode()
                    response = await self.routes[path](
                        method,
                        ujson.loads(body)
                    )
                    content_type = "application/json"
            else:
                try:
                    # 組み込みの open 関数で静的ファイル （HTML, CSS, JS） を読み込む
                    with open(f"www{path}", "r") as f:
                        response = f.read()
                        if path.endswith(".css"):
                            content_type = "text/css"
                        elif path.endswith(".js"):
                            content_type = "application/javascript"
                except FileNotFoundError:
                    status = "404 Not Found"
                    response = "Not Found"

            writer.write(
                (
                    f"HTTP/1.1 {status}\r\n"
                    f"Content-Type: {content_type}\r\n"
                    f"\r\n"
                    f"{response}"
                ).encode()
            )
            await writer.drain()
        except OSError as e:
            if e.args[0] == 104:  # ECONNRESET
                pass  # クライアントが接続をリセットした場合は無視
            else:
                raise  # 他のエラーは再スロー
        finally:
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
        # サーバーオブジェクトを _ に割り当て、未使用であることを明示
        _ = await asyncio.start_server(self.handle_client, "0.0.0.0", 80)
        # サーバーを継続的に実行するためにイベントループを維持
        while True:
            await asyncio.sleep(1)  # 無限ループでサーバーを稼働
