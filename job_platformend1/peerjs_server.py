import asyncio
import websockets
import json
import logging
from websockets import WebSocketServerProtocol

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('PeerJSServer')

class PeerJSServer:
    def __init__(self):
        self.connected_peers = {}

    async def handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        try:
            peer_id = path.split('/')[-1]
            if not peer_id:
                await websocket.close(code=4000, reason="Invalid peer ID")
                return

            self.connected_peers[peer_id] = websocket
            logger.info(f"Peer connected: {peer_id}")

            # Ожидаем сообщения от клиента
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.process_message(peer_id, data, websocket)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from {peer_id}")
                    continue

        except websockets.exceptions.ConnectionClosedOK:
            logger.info(f"Peer {peer_id} disconnected normally")
        except Exception as e:
            logger.error(f"Error with peer {peer_id}: {str(e)}")
        finally:
            self.connected_peers.pop(peer_id, None)
            logger.info(f"Peer {peer_id} removed")

    async def process_message(self, sender_id: str, data: dict, sender_ws: WebSocketServerProtocol):
        if data.get('type') == 'ping':
            await sender_ws.send(json.dumps({'type': 'pong'}))
        elif 'dst' in data:
            # Пересылаем сообщение конкретному получателю
            receiver_id = data['dst']
            if receiver_id in self.connected_peers:
                try:
                    await self.connected_peers[receiver_id].send(json.dumps(data))
                except websockets.exceptions.ConnectionClosed:
                    logger.warning(f"Receiver {receiver_id} disconnected")
            else:
                logger.warning(f"Receiver {receiver_id} not found")
        else:
            logger.warning(f"Unhandled message type from {sender_id}")

async def main():
    server = PeerJSServer()
    start_server = await websockets.serve(
        server.handle_connection,
        "localhost",
        9000,
        ping_interval=20,
        ping_timeout=60,
        max_size=10 * 1024 * 1024,  # 10MB
        origins=None  # Разрешить все origin
    )

    logger.info("PeerJS Server started at ws://localhost:9000")
    await start_server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")