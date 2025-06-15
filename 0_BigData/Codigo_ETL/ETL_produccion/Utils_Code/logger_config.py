# logger_config.py
import logging
import google.cloud.logging

def setup_logging():
    """
    Configura el logging para enviar los registros a Google Cloud Logging.
    """
    # Instancia el cliente de Cloud Logging.
    # La autenticación es automática cuando se ejecuta en un entorno de GCP.
    try:
        client = google.cloud.logging.Client()
        
        # Obtiene el handler por defecto que se integra con el logger de Python.
        handler = client.get_default_handler()
        
        # Configura el logger raíz para usar el handler de GCP.
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(handler)
        
        # Opcional: Reduce el nivel de logging de librerías muy verbosas
        # para no saturar los logs con información de bajo nivel.
        logging.getLogger('google.api_core').setLevel(logging.WARNING)
        logging.getLogger('google.auth').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        
        # Retorna un logger específico para el módulo que lo llama.
        return logging.getLogger(__name__)

    except Exception as e:
        # Si hay un error al configurar el logger de GCP (por ejemplo, al correr localmente
        # sin autenticación), se recurre a un logger básico de consola.
        print(f"ADVERTENCIA: No se pudo configurar Google Cloud Logging. Error: {e}")
        print("Se utilizará el logging básico en la consola.")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

# Se crea una instancia del logger para ser importada por otros módulos.
logger = setup_logging()
