import pandas as pd
from .data_loader import load_expeditions_data
from .logger import setup_logger

logger = setup_logger()

def get_top_clients(limit=5, year=None, month=None):
    """
    Return top clients by total ordered quantity.
    
    Args:
        limit (int): Number of top clients to return (1-8)
        year (int): Year to filter
        month (int): Month to filter
    
    Returns:
        list: List of top client names
    """
    df = load_expeditions_data()
    if df.empty:
        return []
    
    # Apply date filters
    if year:
        df = df[df['fechaTransporte'].dt.year == year]
    if month:
        df = df[df['fechaTransporte'].dt.month == month]
    
    # Group by client and get top by ordered quantity
    logger.info(f"Getting top {limit} clients for year={year}, month={month}")
    client_totals = df.groupby('cliente')['cantidadPedida'].sum().nlargest(limit)
    return client_totals.index.tolist()

def get_client_service_level(client_list, year=None, month=None):
    """
    Calculate service level (shipped/ordered) for given clients.
    
    Args:
        client_list (list): List of client references
        year (int): Year to filter
        month (int): Month to filter
    
    Returns:
        dict: Service levels for each client
    """
    df = load_expeditions_data()
    if df.empty:
        return {}
    
    # Apply filters
    if year:
        df = df[df['fechaTransporte'].dt.year == year]
    if month:
        df = df[df['fechaTransporte'].dt.month == month]
    
    df = df[df['cliente'].isin(client_list)]
    
    service_levels = {}
    for client in client_list:
        client_data = df[df['cliente'] == client]
        total_ordered = client_data['cantidadPedida'].sum()
        total_shipped = client_data['cantidadServida'].sum()
        
        service_level = total_shipped / total_ordered if total_ordered > 0 else 0
        service_levels[client] = round(service_level, 3)
    
    logger.info(f"Calculated service levels for clients: {service_levels}")
    return service_levels

def get_expedition_metrics(client_list, year=None, month=None):
    """
    Return count of expeditions, total ordered, total shipped for given clients.
    
    Args:
        client_list (list): List of client names
        year (int): Year to filter
        month (int): Month to filter
    
    Returns:
        dict: Metrics for each client
    """
    df = load_expeditions_data()
    if df.empty:
        return {}
    
    # Apply filters
    if year:
        df = df[df['fechaTransporte'].dt.year == year]
    if month:
        df = df[df['fechaTransporte'].dt.month == month]
    
    df = df[df['cliente'].isin(client_list)]
    
    metrics = {}
    for client in client_list:
        client_data = df[df['cliente'] == client]
        metrics[client] = {
            'expedition_count': len(client_data),
            'total_ordered': client_data['cantidadPedida'].sum(),
            'total_shipped': client_data['cantidadServida'].sum()
        }
    logger.info(f"Calculated expedition metrics for clients: {metrics}")
    return metrics