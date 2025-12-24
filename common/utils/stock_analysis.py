import pandas as pd
from datetime import datetime
from .data_loader import load_stock_data
from .logger import setup_logger
from typing import List, Dict

logger = setup_logger('common.utils.stock_analysis')

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
    
    reference_totals = df.groupby('Material')['Stock'].sum().nlargest(limit)
    reference_totals = reference_totals.index.tolist()
    reference_totals = [str(ref) for ref in reference_totals]
    logger.info(f"Top references: {reference_totals}")
    return reference_totals

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
    
    df = df[df['Material'].isin(reference_list)]
    
    avg_times = {}
    for ref in reference_list:
        ref_data = df[df['Material'] == ref]
        if not ref_data.empty:
            current_date = datetime.now()
            time_in_warehouse = (current_date - ref_data['Date']).dt.days
            avg_time = time_in_warehouse.mean()
            avg_times[ref] = round(avg_time, 1)
        else:
            avg_times[ref] = 0
    
    avg_times = {str(k): float(v) for k, v in avg_times.items()}
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
    
    df = df[df['Material'].isin(reference_list)]
    
    metrics = {}
    for ref in reference_list:
        ref_data = df[df['Material'] == ref]
        metrics[ref] = {
            'total_pieces': float(ref_data['Stock'].sum()),
            'location_count': int(ref_data['Location'].nunique()),
            'hu_count': int(ref_data['HU'].nunique())
        }
    
    logger.info(f"Calculated stock metrics for references: {metrics}")
    return metrics