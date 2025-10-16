import asyncio
import signal
import sys
import logging
from api.websocket_server import ChatWebSocketServer
from utils.helpers import setup_logging

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

class ChatApplication:
    def __init__(self):
        self.websocket_server = ChatWebSocketServer()
        self.server = None
    
    async def start(self):
        """Inicia la aplicación"""
        try:
            logger.info("🤖 Iniciando Servidor ChatBot con Gemini...")
            self.server = await self.websocket_server.start_server()
            logger.info("✅ Servidor iniciado correctamente")
            logger.info("📡 Esperando conexiones WebSocket...")
        except Exception as e:
            logger.error(f"❌ Error al iniciar servidor: {e}")
            raise
    
    async def stop(self):
        """Detiene la aplicación"""
        logger.info("🛑 Deteniendo servidor...")
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        logger.info("👋 Servidor detenido")

async def main():
    app = ChatApplication()
    
    # Manejar señal de interrupción (Ctrl+C)
    def signal_handler(sig, frame):
        print("\n🛑 Recibida señal de interrupción, deteniendo servidor...")
        asyncio.create_task(app.stop())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await app.start()
        # Mantener el servidor corriendo
        await asyncio.Future()  # run forever
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt")
    except Exception as e:
        logger.error(f"❌ Error en la aplicación: {e}")
    finally:
        await app.stop()

if __name__ == "__main__":
    # Verificar que estamos en el entorno correcto
    print("🚀 Iniciando aplicación...")
    asyncio.run(main())