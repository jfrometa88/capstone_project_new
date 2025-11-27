import pandas as pd
import os
import sys
from datetime import datetime
from .logger import setup_logger

logger = setup_logger()

current_dir = os.path.dirname(os.path.abspath(__file__))

project_root = os.path.abspath(os.path.join(current_dir, '../..'))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

COMMON_DATA_PATH = os.path.join(project_root, "common", "data")

def load_expeditions_data():
    """
    Load and return expeditions data from Excel file.
    
    Returns:
        pandas.DataFrame: Expeditions data with columns:
            - idlinea: int
            - idReferencia: int  
            - referencia: str
            - cantidadPedida: float
            - cantidadServida: float
            - fechaTransporte: datetime
    """    
    try:
        df = pd.read_excel(f'{COMMON_DATA_PATH}/expediciones_test.xlsx')
        df['Date'] = pd.to_datetime(df['Date'])
        df['Client'] = df['Client'].astype(str)
        df['idMaterial'] = df['idMaterial'].astype(str)
        logger.info("Expeditions data loaded successfully.")
        return df
    except Exception as e:
            logger.error(f"Error loading expeditions data: {e}")
            return pd.DataFrame()

def load_stock_data():
    """
    Load and return stock locations data from Excel file.
    
    Returns:
        pandas.DataFrame: Stock data with columns:
            - Ubicación: str
            - referencia: str
            - HU: str
            - Piezas: float
            - Fecha: datetime
    """
    try:
        df = pd.read_excel(f"{COMMON_DATA_PATH}/ubicaciones_test.xlsx")
        df['Date'] = pd.to_datetime(df['Date'])
        logger.info("Stock data loaded successfully.")
        return df
    except Exception as e:
        logger.error(f"Error loading stock data: {e}")
        return pd.DataFrame()