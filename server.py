import os
from aiohttp import web, WSMsgType

web_clients = set()

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    web_clients.add(ws)
    try:
        async for msg in ws:
            pass # Ignore messages from the viewer
    finally:
        web_clients.remove(ws)
    return ws

async def upload_handler(request):
    if request.method == 'POST':
        # Get the Base64 string from the phone
        image_data = await request.text()
        if image_data:
            # Send to all connected viewers
            for ws in web_clients:
                if not ws.closed:
                    await ws.send_str(image_data)
        return web.Response(text="OK")
    return web.Response(status=400)

app = web.Application()
app.router.add_get('/web', websocket_handler)
app.router.add_post('/upload', upload_handler)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, port=port)
