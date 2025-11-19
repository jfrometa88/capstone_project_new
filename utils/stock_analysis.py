import pandas as pd
from datetime import datetime
from .data_loader import load_stock_data
from .logger import setup_logger
from typing import List, Dict

logger = setup_logger()

def get_top_references_stock(limit: int = 5) -> List[str]:
    """
    Return top references by total pieces in stock.
    
    Args:
        limit (int): Number of top references to return (1-8)
    
    Returns:
        List[str]: List of top reference names
    """
    df = load_stock_data()
    if df.empty:
        return []
    
    reference_totals = df.groupby('referencia')['Piezas'].sum().nlargest(limit)
    logger.info(f"Top {limit} references by stock: {reference_totals.index.tolist()}")
    return reference_totals.index.tolist()

def get_avg_time_in_warehouse(reference_list: List[str]) -> Dict[str, float]:
    """
    Calculate average time in warehouse for HUs of given references.
    
    Args:
        reference_list (List[str]): List of reference names
    
    Returns:
        Dict[str, float]: Average time in days for each reference
    """
    df = load_stock_data()
    if df.empty:
        return {}
    
    df = df[df['referencia'].isin(reference_list)]
    
    avg_times = {}
    for ref in reference_list:
        ref_data = df[df['referencia'] == ref]
        if not ref_data.empty:
            current_date = datetime.now()
            time_in_warehouse = (current_date - ref_data['fecha']).dt.days
            avg_time = time_in_warehouse.mean()
            avg_times[ref] = round(avg_time, 1)
        else:
            avg_times[ref] = 0
    
    logger.info(f"Calculated average time in warehouse for references: {avg_times}")
    return avg_times

def get_stock_metrics(reference_list: List[str]) -> Dict[str, dict]:
    """
    Get stock metrics for given references.
    
    Args:
        reference_list (List[str]): List of reference names
    
    Returns:
        Dict[str, dict]: Stock metrics for each reference
    """
    df = load_stock_data()
    if df.empty:
        return {}
    
    df = df[df['referencia'].isin(reference_list)]
    
    metrics = {}
    for ref in reference_list:
        ref_data = df[df['referencia'] == ref]
        metrics[ref] = {
            'total_pieces': ref_data['Piezas'].sum(),
            'location_count': ref_data['Ubicación'].nunique(),
            'hu_count': ref_data['HU'].nunique()
        }
    
    logger.info(f"Calculated stock metrics for references: {metrics}")
    return metrics