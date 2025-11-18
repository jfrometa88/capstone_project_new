import pandas as pd
import numpy as np
from .data_loader import load_expeditions_data, load_stock_data
from .logger import setup_logger

logger = setup_logger()

def get_top_references_expeditions(limit=5, year=None, month=None):
    """
    Return top references by total ordered quantity in expeditions.
    
    Args:
        limit (int): Number of top references to return (1-8)
        year (int): Year to filter
        month (int): Month to filter
    
    Returns:
        list: List of top reference names
    """
    df = load_expeditions_data()
    if df.empty:
        return []
    
    # Apply date filters
    if year:
        df = df[df['fechaTransporte'].dt.year == year]
    if month:
        df = df[df['fechaTransporte'].dt.month == month]
    
    # Group by material reference and get top by ordered quantity
    # Note: In expeditions data, 'referencia' might be client name, 
    # but we need material reference. Assuming 'idReferencia' or similar exists.
    # If not, we might need to adjust based on actual data structure
    reference_totals = df.groupby('idReferencia')['cantidadPedida'].sum().nlargest(limit)
    logger.info(f"Top {limit} references by expeditions: {reference_totals.index.tolist()}")
    return reference_totals.index.tolist()

def get_reference_time_series(reference_list, year=None, month=None):
    """
    Get time series of shipped quantity for given references.
    
    Args:
        reference_list (list): List of reference IDs
        year (int): Year to filter
        month (int): Month to filter
    
    Returns:
        dict: Time series data for each reference
    """
    df = load_expeditions_data()
    if df.empty:
        return {}
    
    # Apply filters
    if year:
        df = df[df['fechaTransporte'].dt.year == year]
    if month:
        df = df[df['fechaTransporte'].dt.month == month]
    
    df = df[df['idReferencia'].isin(reference_list)]
    
    time_series = {}
    for ref in reference_list:
        ref_data = df[df['idReferencia'] == ref]
        monthly_data = ref_data.groupby(ref_data['fechaTransporte'].dt.to_period('M'))['cantidadServida'].sum()
        time_series[ref] = {
            'dates': [str(period) for period in monthly_data.index],
            'quantities': monthly_data.values.tolist()
        }
    logger.info(f"Generated time series for references: {time_series}")
    return time_series

def forecast_next_month_demand(reference_list):
    """
    Simple forecast for next month's demand using moving average.
    
    Args:
        reference_list (list): List of reference IDs
    
    Returns:
        dict: Forecasted demand for each reference
    """
    df = load_expeditions_data()
    if df.empty:
        return {}
    
    df = df[df['idReferencia'].isin(reference_list)]
    
    forecasts = {}
    for ref in reference_list:
        ref_data = df[df['idReferencia'] == ref]
        monthly_data = ref_data.groupby(ref_data['fechaTransporte'].dt.to_period('M'))['cantidadServida'].sum()
        
        if len(monthly_data) >= 3:
            # Use 3-month moving average
            forecast = monthly_data.tail(3).mean()
        elif len(monthly_data) > 0:
            # Use available data average
            forecast = monthly_data.mean()
        else:
            forecast = 0
            
        forecasts[ref] = round(forecast, 2)
    
    logger.info(f"Forecasted next month demand for references: {forecasts}")
    return forecasts