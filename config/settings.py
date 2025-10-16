import os

# Array de tokens de respaldo desde variables de entorno
TOKENS = [
    os.getenv("GEMINI_TOKEN_1", "AIzaSyAXIjZsZeUrzquPThcjQ87zc7pBrLuatYs"),
    os.getenv("GEMINI_TOKEN_2", "AIzaSyCI1KqXGmw8z048cYIWbmJmpUKJHdtevV4")
]

# Filtrar tokens vacíos
TOKENS = [token for token in TOKENS if token and token.strip()]

# Modelos en orden de preferencia
MODELOS = [
    "models/gemini-2.5-flash-lite",
    "models/gemini-2.5-flash"
]

# Configuración del WebSocket
WEBSOCKET_CONFIG = {
    "host": os.getenv("WEBSOCKET_HOST", "0.0.0.0"),
    "port": int(os.getenv("WEBSOCKET_PORT", "8765")),
    "ping_interval": 30,
    "ping_timeout": 10
}

# Configuración de logging
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}