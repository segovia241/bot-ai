import json
import logging
from datetime import datetime

def setup_logging():
    """Configura el logging de la aplicación"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def format_timestamp():
    """Formatea la fecha y hora actual"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def validate_message(data):
    """Valida la estructura del mensaje"""
    required_fields = ["type", "message"]
    
    if not isinstance(data, dict):
        return False, "El mensaje debe ser un objeto JSON"
    
    for field in required_fields:
        if field not in data:
            return False, f"Campo requerido faltante: {field}"
    
    return True, ""

def create_system_message(message_type, **kwargs):
    """Crea un mensaje del sistema"""
    base_message = {
        "type": message_type,
        "timestamp": format_timestamp(),
        "success": True
    }
    base_message.update(kwargs)
    return base_message