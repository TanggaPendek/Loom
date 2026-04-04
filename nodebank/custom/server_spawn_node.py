import subprocess
import sys
import tempfile
import os

def spawn_server_node(server_config: dict, routes) -> int:

    if isinstance(routes, dict):
        routes = [routes]
    elif isinstance(routes, list):
        flat = []
        for r in routes:
            if isinstance(r, list):
                flat.extend(r)
            else:
                flat.append(r)
        routes = flat
    else:
        routes = []

    host = server_config.get("host", "0.0.0.0")
    port = int(server_config.get("port", 8080))
    cors = server_config.get("cors", {})

    if cors.get("enabled"):
        origins = cors.get("origins", "*")
        methods = ",".join(cors.get("methods", ["GET"]))
        cors_block = (
            f'self.send_header("Access-Control-Allow-Origin", "{origins}");'
            f'self.send_header("Access-Control-Allow-Methods", "{methods}");'
            f'self.send_header("Access-Control-Allow-Headers", "Content-Type")'
        )
    else:
        cors_block = ""

    # build route table lines for the banner
    route_lines = []
    for r in routes:
        route_lines.append(f"  {r.get('method','GET'):<8} {r.get('path','/')}  ->  {r.get('status',200)}")
    route_table = "\\n".join(route_lines)

    branches = []
    for i, route in enumerate(routes):
        path   = route.get("path", "/")
        method = route.get("method", "GET")
        status = int(route.get("status", 200))
        body   = route.get("body", "")
        kw     = "if" if i == 0 else "elif"
        branches.append(
            f'        {kw} self.path=={repr(path)} and self.command=={repr(method)}: self._respond({status},{repr(body)})'
        )
    branches.append('        else: self._respond(404,"not found")')
    dispatch_block = "\n".join(branches)

    cors_status = f"enabled (origins={cors.get('origins','*')})" if cors.get("enabled") else "disabled"

    lines = [
        "import http.server,socketserver,signal,os,datetime",
        "signal.signal(signal.SIGTERM,lambda *_:os._exit(0))",
        f"HOST={repr(host)}",
        f"PORT={port}",
        "REQ_COUNT=0",
        "START_TIME=datetime.datetime.now()",

        # banner
        "os.system('cls')",
        r"print('\033[96m' + '='*52 + '\033[0m')",
        r"print('\033[96m   LOOM NODE SERVER\033[0m')",
        r"print('\033[96m' + '='*52 + '\033[0m')",
        f"print(f'  \\033[93mHost  \\033[0m: {host}')",
        f"print(f'  \\033[93mPort  \\033[0m: {port}')",
        f"print(f'  \\033[93mCORS  \\033[0m: {cors_status}')",
        r"print(f'  \033[93mPID   \033[0m: {os.getpid()}')",
        r"print('\033[96m' + '-'*52 + '\033[0m')",
        r"print('\033[97m  ROUTES\033[0m')",
        f"print('{route_table}')",
        r"print('\033[96m' + '-'*52 + '\033[0m')",
        r"print('\033[92m  Server is running -- press Ctrl+C to stop\033[0m')",
        r"print('\033[96m' + '='*52 + '\033[0m')",
        r"print()",

        "class Handler(http.server.BaseHTTPRequestHandler):",
        "    def _respond(self,status,body):",
        "        global REQ_COUNT",
        "        REQ_COUNT+=1",
        "        encoded=body.encode() if isinstance(body,str) else body",
        "        self.send_response(status)",
        '        self.send_header("Content-Type","text/plain")',
        '        self.send_header("Content-Length",str(len(encoded)))',
        f"        {cors_block}" if cors_block else "        pass",
        "        self.end_headers()",
        "        self.wfile.write(encoded)",
        "    def do_GET(self): self._dispatch()",
        "    def do_POST(self): self._dispatch()",
        "    def do_OPTIONS(self): self._respond(204,'')",
        "    def _dispatch(self):",
        dispatch_block,
        "    def log_message(self,fmt,*args):",
        "        now=datetime.datetime.now().strftime('%H:%M:%S')",
        "        addr=self.address_string()",
        r"        print(f'  \033[90m[{now}]\033[0m \033[97m{addr}\033[0m  {fmt%args}  \033[90m(req #{REQ_COUNT})\033[0m',flush=True)",

        "socketserver.TCPServer.allow_reuse_address=True",
        "srv=socketserver.TCPServer((HOST,PORT),Handler)",
        "srv.serve_forever()",
    ]

    script = "\n".join(lines)

    script_path = os.path.join(tempfile.gettempdir(), "spawned_server.py")
    with open(script_path, "w") as f:
        f.write(script)

    python = sys.executable

    proc = subprocess.Popen(
        ["powershell", "-NoExit", "-Command", f'& "{python}" "{script_path}"'],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )

    print(f"[server_launch] pid={proc.pid}  {host}:{port}  routes={len(routes)}")
    return proc.pid