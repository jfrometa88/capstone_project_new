import pandas as pd
from .data_loader import load_expeditions_data
from .logger import setup_logger
from typing import List, Dict

logger = setup_logger()

def get_top_clients(month: int = 0, limit: int = 5, year: int = 2025) -> List[str]:
    """
    Return top clients by total ordered quantity.
    If month or year is not provided, do not filter by that field.
    
    Args:
        month (int): Month to filter, if 0, no filter
        limit (int): Number of top clients to return (1-8)
        year (int): Year to filter
        
    
    Returns:
        List[str]: List of top client names
    """
    df = load_expeditions_data()
    if df.empty:
        return []
    
    subs_month = month

    if subs_month == 0:
        subs_month = None

    # Apply date filters
    if year:
        df = df[df['fechaTransporte'].dt.year == year]
    if subs_month:
        df = df[df['fechaTransporte'].dt.month == month]
    
    # Group by client and get top by ordered quantity
    logger.info(f"Getting top {limit} clients for year={year}, month={month}")
    client_totals = df.groupby('cliente')['cantidadPedida'].sum().nlargest(limit)
    client_totals = client_totals.index.tolist()
    client_totals = [str(client) for client in client_totals]
    logger.info(f"Top clients: {client_totals}")
    return client_totals

def get_client_service_level(month: int, client_list: List[str], year: int = 2025) -> Dict[str, float]:
    """
    Calculate service level (shipped/ordered) for given clients.
    
    Args:
        month (int): Month to filter, if 0, no filter
        client_list (List[str]): List of client references
        year (int): Year to filter
    
    Returns:
        Dict[str, float]: Service levels for each client 
    """
    df = load_expeditions_data()
    if df.empty:
        return {}
    
    subs_month = month
    if subs_month == 0:
        subs_month = None

    # Apply filters
    if year:
        df = df[df['fechaTransporte'].dt.year == year]
    if subs_month:
        df = df[df['fechaTransporte'].dt.month == month]
    
    df = df[df['cliente'].isin(client_list)]
    
    service_levels = {}
    for client in client_list:
        client_data = df[df['cliente'] == client]
        total_ordered = client_data['cantidadPedida'].sum()
        total_shipped = client_data['cantidadServida'].sum()
        
        service_level = total_shipped / total_ordered if total_ordered > 0 else 0
        service_levels[client] = round(service_level, 3)
    
    service_levels = {str(k): float(v) for k, v in service_levels.items()}
    logger.info(f"Calculated service levels for clients: {service_levels}")
    return service_levels

def get_expedition_metrics(month: int, client_list: List[str], year: int = 2025, )-> Dict[str, dict]:
    """
    Return count of expeditions, total ordered, total shipped for given clients.
    
    Args:
        month (int): Month to filter, if 0, no filter
        client_list (List[str]): List of client names
        year (int): Year to filter
        
    
    Returns:
        Dict[str, dict]: Metrics for each client
    """
    df = load_expeditions_data()
    if df.empty:
        return {}
    
    subs_month = month
    if subs_month == 0:
        subs_month = None

    # Apply filters
    if year:
        df = df[df['fechaTransporte'].dt.year == year]
    if subs_month:
        df = df[df['fechaTransporte'].dt.month == month]
    
    df = df[df['cliente'].isin(client_list)]
    
    metrics = {}
    for client in client_list:
        client_data = df[df['cliente'] == client]
        metrics[client] = {
            'expedition_count': int(len(client_data)),
            'total_ordered': float(client_data['cantidadPedida'].sum()),
            'total_shipped': float(client_data['cantidadServida'].sum())
        }
    logger.info(f"Calculated expedition metrics for clients: {metrics}")
    return metrics