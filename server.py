import os
import asyncio
import websockets

clients = {"phone": None, "web": set()}

async def handler(ws, path):
    role = path.strip('/')
    
    if role == 'phone':
        clients['phone'] = ws
        try:
            async for message in ws:
                for web_client in list(clients['web']):
                    try:
                        await web_client.send(message)
                    except:
                        clients['web'].discard(web_client)
        finally:
            clients['phone'] = None
            
    elif role == 'web':
        clients['web'].add(ws)
        try:
            await ws.wait_closed()
        finally:
            clients['web'].discard(ws)

async def main():
    port = int(os.environ.get("PORT", 8765))
    async with websockets.serve(handler, "0.0.0.0", port, max_size=None):
        print(f"Server running on port {port}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
