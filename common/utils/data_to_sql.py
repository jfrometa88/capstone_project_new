import pandas as pd
import os
import sys
import sqlite3

current_dir = os.path.dirname(os.path.abspath(__file__))

project_root = os.path.abspath(os.path.join(current_dir, "../.."))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

COMMON_DATA_PATH = os.path.join(project_root, "common", "data")

from common.utils.logger import setup_logger
from common.utils.data_loader import load_expeditions_data, load_stock_data

logger = setup_logger('common.utils.data_to_sql')

df_expeditions = load_expeditions_data()
df_stock = load_stock_data()

def dataframes_to_sql(df_expeditions:pd.DataFrame=df_expeditions, df_stock:pd.DataFrame=df_stock)->None:
    """
    Save expeditions and stock dataframes to SQL database.

    """
    with sqlite3.connect(f"{COMMON_DATA_PATH}/logistics_data.db") as conn:
        try:
            cursor = conn.cursor()
            logger.info("Connected to the database successfully.")
            create_table_query = '''
            CREATE TABLE IF NOT EXISTS Expediciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idLine TEXT NOT NULL,
                idMaterial TEXT NOT NULL,
                Material TEXT,
                Purchased REAL,
                Served REAL,
                Client TEXT,
                Date TEXT,    
                date_inserted TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            '''
            cursor.execute(create_table_query)
            conn.commit()
            logger.info("Ensured Expediciones table exists.")
        except sqlite3.Error as e:
            logger.error(f"Database Expediciones error: {e}")

        try:
            
            create_table_query = '''
            CREATE TABLE IF NOT EXISTS Ubicaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Location TEXT NOT NULL,
                Material TEXT,
                HU TEXT,
                Stock REAL,
                Date TEXT,    
                date_inserted TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            '''
            cursor.execute(create_table_query)
            conn.commit()
            logger.info("Ensured Ubicaciones table exists.")
        except sqlite3.Error as e:
            logger.error(f"Database Ubicaciones error: {e}")

        try:
            df_exp_db = pd.read_sql_query("SELECT idLine, idMaterial, Date FROM Expediciones", conn)
            df_ubi_db = pd.read_sql_query("SELECT Location, Material, HU, Date FROM Ubicaciones", conn)
            
            logger.info("Fetched existing records from database.")
            set_lineas = set(df_exp_db['idLine'].astype(int))
            
            set_ubicaciones = set(zip(df_ubi_db['Location'], df_ubi_db['Material'], df_ubi_db['HU']))

            new_expeditions = df_expeditions[~df_expeditions['idLine'].isin(set_lineas)]
            
            new_stock = df_stock[~df_stock.apply(lambda row: (row['Location'], row['Material'], row['HU']), axis=1).isin(set_ubicaciones)]

            if not new_expeditions.empty:
                new_expeditions.to_sql('Expediciones', conn, if_exists='append', index=False)
                logger.info(f"Inserted {len(new_expeditions)} new expeditions records.")
            else:
                logger.info("No new expeditions records to insert.")

            if not new_stock.empty:
                new_stock.to_sql('Ubicaciones', conn, if_exists='append', index=False)
                logger.info(f"Inserted {len(new_stock)} new stock records.")
            else:
                logger.info("No new stock records to insert.")
        except Exception as e:
            logger.error(f"Error inserting data into database: {e}")
    logger.info("Database connection closed.")

if __name__ == "__main__":
    dataframes_to_sql(df_expeditions, df_stock)
          
