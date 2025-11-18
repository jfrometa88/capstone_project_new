import logging
import os
from datetime import datetime
import functools

def setup_logger():
    """Configurar el sistema de logging"""
    
    # Crear directorio de logs si no existe
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Nombre del archivo con fecha
    log_filename = f"logs/dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # También muestra en consola
        ]
    )
    
    return logging.getLogger('dashboard')

# Inicializar logger
logger = setup_logger()