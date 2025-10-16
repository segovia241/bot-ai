import google.generativeai as genai
import asyncio
import logging
from config.settings import TOKENS, MODELOS

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        self.modelos_configurados = []
        self.inicializar_modelos()
        # Sistema de prompts para respuestas concisas
        self.system_prompt = """
        Eres un asistente útil y directo. Sigue estas pautas estrictamente:
        
        - Sé conciso y ve al punto principal
        - Limita las respuestas a 2-3 párrafos como máximo
        - Evita introducciones largas o despedidas elaboradas
        - Usa lenguaje claro y directo
        - Estructura la información de manera organizada pero breve
        - Si es necesario dividir información, usa puntos breves
        - Responde directamente a la pregunta sin rodeos
        
        El usuario valora la precisión y brevedad.
        """
    
    def inicializar_modelos(self):
        """Configura todos los modelos al inicio del programa"""
        self.modelos_configurados = []
        
        if not TOKENS:
            logger.error("❌ No se encontraron tokens de API configurados")
            return
        
        for modelo in MODELOS:
            for token in TOKENS:
                try:
                    # Configurar y crear instancia UNA sola vez
                    genai.configure(api_key=token)
                    model = genai.GenerativeModel(modelo)
                    self.modelos_configurados.append({
                        'model': model,
                        'model_name': modelo,
                        'token': token  # Guardamos el token completo para usar en las requests
                    })
                    logger.info(f"✅ Modelo configurado: {modelo}")
                except Exception as e:
                    logger.warning(f"❌ Error configurando {modelo}: {e}")
                    continue
    
    async def procesar_texto(self, texto_usuario: str):
        """Procesa el texto usando los modelos pre-configurados"""
        
        if not self.modelos_configurados:
            return {
                "success": False,
                "error": "No hay modelos configurados disponibles"
            }
        
        # Combinar el system prompt con el mensaje del usuario
        prompt_completo = f"{self.system_prompt}\n\nPregunta del usuario: {texto_usuario}"
        
        # Intentar con cada modelo pre-configurado
        for config in self.modelos_configurados:
            try:
                # Configurar el token antes de cada request por si hay cambios
                genai.configure(api_key=config['token'])
                
                # Usar la instancia ya creada
                response = await config['model'].generate_content_async(prompt_completo)
                logger.info(f"✅ Respuesta exitosa con: {config['model_name']}")
                return {
                    "success": True,
                    "response": response.text,
                    "model_used": config['model_name']
                }
            except Exception as e:
                logger.warning(f"❌ Error con {config['model_name']}: {e}")
                continue
        
        return {
            "success": False,
            "error": "No se pudo procesar el texto con ningún modelo disponible"
        }
    
    def get_status(self):
        """Retorna el estado del cliente"""
        return {
            "modelos_configurados": len(self.modelos_configurados),
            "modelos_disponibles": [config['model_name'] for config in self.modelos_configurados],
            "tokens_disponibles": len(TOKENS)
        }