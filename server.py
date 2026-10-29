import os
from aiohttp import web

web_clients = set()

async def home_handler(request):
    return web.Response(text="Ludo Stream Server is Running perfectly!")

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    web_clients.add(ws)
    print("Website Viewer Connected")
    try:
        async for msg in ws:
            pass
    finally:
        web_clients.remove(ws)
        print("Website Viewer Disconnected")
    return ws

async def upload_handler(request):
    if request.method == 'POST':
        try:
            image_data = await request.text()
            if image_data:
                # Print size to server logs for debugging
                print(f"Received image data (Size: {len(image_data)} bytes)")
                
                for ws in list(web_clients):
                    if not ws.closed:
                        try:
                            await ws.send_str(image_data)
                        except:
                            pass
            return web.Response(text="OK")
        except Exception as e:
            print(f"Error: {e}")
            return web.Response(status=500, text="Error")
    return web.Response(status=400)

app = web.Application()
# THIS LINE PREVENTS THE SERVER FROM BLOCKING LARGE IMAGES
app.client_max_size = 10 * 1024 * 1024 
app.router.add_get('/', home_handler)
app.router.add_get('/web', websocket_handler)
app.router.add_post('/upload', upload_handler)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, port=port)
