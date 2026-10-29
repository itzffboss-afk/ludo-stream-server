import os
from aiohttp import web

web_clients = set()

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Ludo Stream Viewer</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@600;800&display=swap" rel="stylesheet">
    <style>
        :root { --bg: #06090f; --primary: #38bdf8; --success: #10b981; --danger: #ef4444; --text: #f8fafc; --text-dim: #64748b; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background-color: var(--bg); color: var(--text); font-family: 'Plus Jakarta Sans', sans-serif; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
        .top-bar { background: rgba(15, 23, 42, 0.9); padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); z-index: 10; }
        .brand { font-size: 16px; font-weight: 800; }
        .brand span { color: var(--primary); font-size: 12px; display: block; }
        .status-pill { background: rgba(239, 68, 68, 0.2); color: var(--danger); padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; font-family: 'JetBrains Mono', monospace; border: 1px solid rgba(239, 68, 68, 0.3); }
        .status-pill.live { background: rgba(16, 185, 129, 0.2); color: var(--success); border-color: rgba(16, 185, 129, 0.3); box-shadow: 0 0 15px rgba(16, 185, 129, 0.2); }
        .status-pill.connecting { background: rgba(245, 158, 11, 0.2); color: #f59e0b; border-color: rgba(245, 158, 11, 0.3); animation: pulse 1s infinite alternate; }
        @keyframes pulse { from { opacity: 0.5; } to { opacity: 1; } }
        .stream-container { flex: 1; display: flex; justify-content: center; align-items: center; position: relative; padding: 10px; }
        #screen { max-width: 100%; max-height: 100%; border-radius: 12px; box-shadow: 0 0 40px rgba(0,0,0,0.8); display: none; border: 2px solid rgba(56, 189, 248, 0.3); }
        #loader { display: flex; flex-direction: column; align-items: center; justify-content: center; position: absolute; }
        .spinner { width: 50px; height: 50px; border: 4px solid rgba(56, 189, 248, 0.1); border-top: 4px solid var(--primary); border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 20px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        #loader-text { font-family: 'JetBrains Mono', monospace; color: var(--text-dim); font-size: 13px; text-align: center; }
        #counter { position: absolute; top: 10px; right: 10px; color: #fff; background: #000; padding: 5px 10px; border-radius: 10px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="top-bar">
        <div class="brand">Ludo Stream<span>TACTICAL VIEWER</span></div>
        <div class="status-pill connecting" id="status">CONNECTING...</div>
    </div>
    <div id="counter">Frames: 0</div>
    <div class="stream-container">
        <div id="loader">
            <div class="spinner"></div>
            <div id="loader-text">Waiting for Game Phone...</div>
        </div>
        <img id="screen" src="" />
    </div>

    <script>
        const SERVER_URL = "wss://" + window.location.host + "/web"; 
        let ws;
        let frames = 0;
        const img = document.getElementById('screen');
        const status = document.getElementById('status');
        const loader = document.getElementById('loader');
        const counter = document.getElementById('counter');

        function connect() {
            status.innerText = "CONNECTING...";
            status.className = "status-pill connecting";
            ws = new WebSocket(SERVER_URL);

            ws.onopen = () => {
                status.innerText = "WAITING FOR PHONE...";
                status.className = "status-pill connecting";
            };

            ws.onmessage = (event) => {
                if (event.data === "TEST") return; // Ignore test messages
                
                frames++;
                counter.innerText = "Frames: " + frames;

                if (img.style.display === 'none') {
                    img.style.display = 'block';
                    loader.style.display = 'none';
                    status.innerText = "LIVE STREAM";
                    status.className = "status-pill live";
                }
                img.src = "data:image/jpeg;base64," + event.data;
            };

            ws.onclose = () => {
                status.innerText = "DISCONNECTED";
                status.className = "status-pill";
                img.style.display = 'none';
                loader.style.display = 'flex';
                setTimeout(connect, 3000);
            };
            ws.onerror = () => { ws.close(); };
        }
        connect();
    </script>
</body>
</html>
"""

async def home_handler(request):
    return web.Response(text=html_code, content_type='text/html')

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    web_clients.add(ws)
    # Send a test message so the browser knows the connection is alive
    await ws.send_str("TEST")
    try:
        async for msg in ws:
            pass
    finally:
        web_clients.remove(ws)
    return ws

async def upload_handler(request):
    if request.method == 'POST':
        try:
            image_data = await request.text()
            if image_data:
                for ws in list(web_clients):
                    if not ws.closed:
                        try:
                            await ws.send_str(image_data)
                        except Exception:
                            pass
            return web.Response(text="OK")
        except Exception:
            return web.Response(status=500, text="Error")
    return web.Response(status=400)

app = web.Application()
app.client_max_size = 10 * 1024 * 1024 
app.router.add_get('/', home_handler)
app.router.add_get('/web', websocket_handler)
app.router.add_post('/upload', upload_handler)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, port=port)
