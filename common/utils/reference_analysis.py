import pandas as pd
import numpy as np
from .data_loader import load_expeditions_data, load_stock_data
from .logger import setup_logger
from typing import List, Dict

logger = setup_logger()

def get_top_references_expeditions(month: int = 0, limit: int = 5, year: int = 2025) -> List[str]:
    """
    Return top references by total ordered quantity in expeditions.
    
    Args:
        month (int): Month to filter, if 0, no filter
        limit (int): Number of top references to return (1-8)
        year (int): Year to filter        
    
    Returns:
        List[str]: List of top reference names
    """
    df = load_expeditions_data()
    if df.empty:
        return []
    
    sub_month = month
    if sub_month == 0:
        sub_month = None
    
    # Apply date filters
    if year:
        df = df[df['Date'].dt.year == year]
    if sub_month:
        df = df[df['Date'].dt.month == month]
    
    # Group by material reference and get top by ordered quantity
    # Note: In expeditions data, 'referencia' might be client name, 
    # but we need material reference. Assuming 'idReferencia' or similar exists.
    # If not, we might need to adjust based on actual data structure
    reference_totals = df.groupby('idMaterial')['Purchased'].sum().nlargest(limit)
    logger.info(f"Top {limit} references by expeditions: {reference_totals.index.tolist()}")
    reference_totals = reference_totals.index.tolist()
    reference_totals = [str(ref) for ref in reference_totals]
    logger.info(f"Top references: {reference_totals}")
    return reference_totals

def get_reference_time_series(month: int, reference_list: List[str], year: int = 2025) -> Dict[str, dict]:
    """
    Get time series of shipped quantity for given references.
    
    Args:
        month (int): Month to filter, if 0, no filter
        reference_list (list): List of reference IDs
        year (int): Year to filter        
    
    Returns:
        Dict[str, dict]: Time series data for each reference
    """
    df = load_expeditions_data()
    if df.empty:
        return {}
    
    sub_month = month
    if sub_month == 0:
        sub_month = None

    # Apply filters
    if year:
        df = df[df['Date'].dt.year == year]
    if sub_month:
        df = df[df['Date'].dt.month == month]
    
    df = df[df['idMaterial'].isin(reference_list)]
    
    time_series = {}
    for ref in reference_list:
        ref_data = df[df['idMaterial'] == ref]
        monthly_data = ref_data.groupby(ref_data['Date'].dt.to_period('M'))['Served'].sum()
        time_series[ref] = {
            'dates': [str(period) for period in monthly_data.index],
            'quantities': [float(i) for i in monthly_data.values.tolist()]
        }
    logger.info(f"Generated time series for references: {time_series}")
    return time_series

def forecast_next_month_demand(reference_list: List[str]) -> Dict[str, float]:
    """
    Simple forecast for next month's demand using moving average.
    
    Args:
        reference_list (List[str]): List of reference IDs
    
    Returns:
        Dict[str, float]: Forecasted demand for each reference
    """
    df = load_expeditions_data()
    if df.empty:
        return {}
    
    df = df[df['idMaterial'].isin(reference_list)]
    
    forecasts = {}
    for ref in reference_list:
        ref_data = df[df['idMaterial'] == ref]
        monthly_data = ref_data.groupby(ref_data['Date'].dt.to_period('M'))['Served'].sum()
        
        if len(monthly_data) >= 3:
            # Use 3-month moving average
            forecast = monthly_data.tail(3).mean()
        elif len(monthly_data) > 0:
            # Use available data average
            forecast = monthly_data.mean()
        else:
            forecast = 0
            
        forecasts[ref] = round(forecast, 2)
    forecasts = {str(k): float(v) for k, v in forecasts.items()}
    
    logger.info(f"Forecasted next month demand for references: {forecasts}")
    return forecasts