import pandas as pd
from datetime import datetime
from .data_loader import stock_data_sql
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
    df = stock_data_sql()
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
    df = stock_data_sql()
    if df.empty:
        return {}

    df_filtered = df[df['Material'].isin(reference_list)].copy()

    current_date = datetime.now()
    
    # Calcular días para todos de golpe (Vectorizado)
    df_filtered['days'] = (current_date - df_filtered['Date']).dt.days
    
    # Agrupar y calcular media
    result = df_filtered.groupby('Material')['days'].mean().round(1).to_dict()
    avg_times = {str(k): float(v) for k, v in result.items()}
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
    df = stock_data_sql()
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