import pandas as pd
from datetime import datetime
from .logger import setup_logger

logger = setup_logger()

COMMON_DATA_PATH = "/common/data"
COMMON_DATA_PATH1 = "common/data"

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
    except:
        try:
            df = pd.read_excel(f'{COMMON_DATA_PATH1}/expediciones_test.xlsx')
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
    except:
        try:
            df = pd.read_excel(f"{COMMON_DATA_PATH1}/ubicaciones_test.xlsx")
            df['Date'] = pd.to_datetime(df['Date'])
            logger.info("Stock data loaded successfully.")
            return df
        except Exception as e:
            logger.error(f"Error loading stock data: {e}")
            return pd.DataFrame()