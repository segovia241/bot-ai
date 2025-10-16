import asyncio
from functools import partial
import websockets
import json
import logging
from models.gemini_client import GeminiClient
from config.settings import WEBSOCKET_CONFIG

logger = logging.getLogger(__name__)

class ChatWebSocketServer:
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.connected_clients = set()
    
    async def handle_client_message(self, websocket, message):
        """Maneja un mensaje individual del cliente"""
        try:
            data = json.loads(message)
            message_type = data.get("type", "message")
            
            if message_type == "chat_message":
                user_message = data.get("message", "").strip()
                
                if not user_message:
                    await self.send_error(websocket, "El mensaje no puede estar vacío")
                    return
                
                # Enviar confirmación de recepción
                await self.send_message(websocket, {
                    "type": "message_received",
                    "message": user_message
                })
                
                # Procesar con Gemini
                result = await self.gemini_client.procesar_texto(user_message)
                
                if result["success"]:
                    await self.send_message(websocket, {
                        "type": "chat_response",
                        "message": result["response"],
                        "model_used": result["model_used"],
                        "success": True
                    })
                else:
                    await self.send_error(websocket, result["error"])
                    
            elif message_type == "status":
                # Enviar estado del servidor
                status = self.gemini_client.get_status()
                await self.send_message(websocket, {
                    "type": "status",
                    "status": status
                })
                
            else:
                await self.send_error(websocket, f"Tipo de mensaje no reconocido: {message_type}")
                
        except json.JSONDecodeError:
            await self.send_error(websocket, "Formato JSON inválido")
        except Exception as e:
            logger.error(f"Error manejando mensaje: {e}")
            await self.send_error(websocket, f"Error interno del servidor: {str(e)}")
    
    async def send_message(self, websocket, data):
        """Envía un mensaje al cliente"""
        try:
            await websocket.send(json.dumps(data))
        except Exception as e:
            logger.error(f"Error enviando mensaje: {e}")
    
    async def send_error(self, websocket, error_message):
        """Envía un mensaje de error al cliente"""
        await self.send_message(websocket, {
            "type": "error",
            "message": error_message,
            "success": False
        })
    
    async def websocket_handler(self, websocket):
        """Handler principal del WebSocket (versión moderna websockets)"""
        self.connected_clients.add(websocket)
        client_info = f"{websocket.remote_address}"
        logger.info(f"✅ Cliente conectado: {client_info}")

        try:
            await self.send_message(websocket, {
                "type": "connection_established",
                "message": "Conexión WebSocket establecida correctamente",
                "status": self.gemini_client.get_status()
            })

            async for message in websocket:
                await self.handle_client_message(websocket, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 Cliente desconectado: {client_info}")
        except Exception as e:
            logger.error(f"❌ Error con cliente {client_info}: {e}")
        finally:
            self.connected_clients.remove(websocket)

    
    async def start_server(self):
        """Inicia el servidor WebSocket"""
        server = await websockets.serve(
            partial(self.websocket_handler),
            WEBSOCKET_CONFIG["host"],
            WEBSOCKET_CONFIG["port"],
            ping_interval=WEBSOCKET_CONFIG["ping_interval"],
            ping_timeout=WEBSOCKET_CONFIG["ping_timeout"]
        )

        logger.info(f"🚀 Servidor WebSocket iniciado en ws://{WEBSOCKET_CONFIG['host']}:{WEBSOCKET_CONFIG['port']}")
        logger.info(f"📊 Modelos configurados: {len(self.gemini_client.modelos_configurados)}")
        return server