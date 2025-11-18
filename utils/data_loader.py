import pandas as pd
from datetime import datetime
from .logger import setup_logger

logger = setup_logger()

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
        df = pd.read_excel('data/expediciones_test.xlsx')
        df['fechaTransporte'] = pd.to_datetime(df['fechaTransporte'])
        df['cliente'] = df['cliente'].astype(str)
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
        df = pd.read_excel('data/ubicaciones_test.xlsx')
        df['fecha'] = pd.to_datetime(df['fecha'])
        logger.info("Stock data loaded successfully.")
        return df
    except Exception as e:
        logger.error(f"Error loading stock data: {e}")
        return pd.DataFrame()