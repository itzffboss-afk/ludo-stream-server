import os
from aiohttp import web

# Store connected web viewers
web_clients = set()

async def home_handler(request):
    # This allows you to visit the site in a browser and see it's alive
    return web.Response(text="Ludo Stream Server is Running perfectly!")

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    web_clients.add(ws)
    print("Website Viewer Connected")
    try:
        async for msg in ws:
            pass # We don't expect messages from the viewer
    finally:
        web_clients.remove(ws)
        print("Website Viewer Disconnected")
    return ws

async def upload_handler(request):
    if request.method == 'POST':
        image_data = await request.text()
        if image_data:
            # Broadcast the image to all connected websites
            for ws in list(web_clients):
                if not ws.closed:
                    try:
                        await ws.send_str(image_data)
                    except:
                        pass
        return web.Response(text="OK")
    return web.Response(status=400)

app = web.Application()
app.router.add_get('/', home_handler)
app.router.add_get('/web', websocket_handler)
app.router.add_post('/upload', upload_handler)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on port {port}")
    web.run_app(app, port=port)
