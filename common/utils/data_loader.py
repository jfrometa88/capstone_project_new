import pandas as pd
import os
import sys
import sqlite3
from .logger import setup_logger
from functools import lru_cache

logger = setup_logger('common.utils.data_loader')

current_dir = os.path.dirname(os.path.abspath(__file__))

project_root = os.path.abspath(os.path.join(current_dir, "../.."))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

COMMON_DATA_PATH = os.path.join(project_root, "common", "data")


def load_expeditions_data():
    """
    Load and return expeditions data from Excel file.

    Returns:
        pandas.DataFrame: Expeditions data with columns:
            - idLine: int
            - idMaterial: int
            - Material: str
            - Purchased: float
            - Served: float
            - Client: str
            - Date: datetime
    """
    try:
        df = pd.read_excel(f"{COMMON_DATA_PATH}/expediciones_test.xlsx")
        df["Date"] = pd.to_datetime(df["Date"])
        df["Client"] = df["Client"].astype(str)
        df["idMaterial"] = df["idMaterial"].astype(str)
        df["Purchased"] = pd.to_numeric(df["Purchased"], errors="coerce").fillna(0)
        df["Served"] = pd.to_numeric(df["Served"], errors="coerce").fillna(0)
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
            - Location: str
            - Material: str
            - HU: str
            - Stock: float
            - Date: datetime
    """
    try:
        df = pd.read_excel(f"{COMMON_DATA_PATH}/ubicaciones_test.xlsx")
        df["Date"] = pd.to_datetime(df["Date"])
        df["Stock"] = pd.to_numeric(df["Stock"], errors="coerce").fillna(0)
        logger.info("Stock data loaded successfully.")
        return df
    except Exception as e:
        logger.error(f"Error loading stock data: {e}")
        return pd.DataFrame()

@lru_cache(maxsize=1)
def expeditions_data_sql()->pd.DataFrame:
    """
    Load and return expeditions data from SQL database.

    Returns:
        pandas.DataFrame: Expeditions data
    """
    try:
        with sqlite3.connect(f"{COMMON_DATA_PATH}/logistics_data.db") as conn:
            df = pd.read_sql_query("SELECT * FROM Expediciones", conn)
            df["Date"] = pd.to_datetime(df["Date"])
            df["Client"] = df["Client"].astype(str)
            df["idMaterial"] = df["idMaterial"].astype(str)
            df["Purchased"] = pd.to_numeric(df["Purchased"], errors="coerce").fillna(0)
            df["Served"] = pd.to_numeric(df["Served"], errors="coerce").fillna(0)
            logger.info("Expeditions data loaded from SQL database successfully.")
            return df
    except Exception as e:
        logger.error(f"Error loading expeditions data from SQL database: {e}")
        return pd.DataFrame()

@lru_cache(maxsize=1)
def stock_data_sql()->pd.DataFrame:
    """
    Load and return stock data from SQL database.

    Returns:
        pandas.DataFrame: Stock data
    """
    try:
        with sqlite3.connect(f"{COMMON_DATA_PATH}/logistics_data.db") as conn:
            df = pd.read_sql_query("SELECT * FROM Ubicaciones", conn)
            df["Date"] = pd.to_datetime(df["Date"])
            df["Stock"] = pd.to_numeric(df["Stock"], errors="coerce").fillna(0)
            logger.info("Stock data loaded from SQL database successfully.")
            return df
    except Exception as e:
        logger.error(f"Error loading stock data from SQL database: {e}")
        return pd.DataFrame()