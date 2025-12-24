from .data_loader import expeditions_data_sql, stock_data_sql
from .logger import setup_logger
from typing import List, Dict, Optional

logger = setup_logger('common.utils.expedition_analysis')


def get_top_clients(
    month: Optional[int] = None, limit: int = 5, year: Optional[int] = None
) -> List[str]:
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
    df = expeditions_data_sql()
    if df.empty:
        return []

    # Apply date filters
    if year:
        df = df[df["Date"].dt.year == year]  # type: ignore
    if month:
        df = df[df["Date"].dt.month == month]  # type: ignore

    # Group by client and get top by ordered quantity
    logger.info(f"Getting top {limit} clients for year={year}, month={month}")
    client_totals = df.groupby("Client")["Purchased"].sum().nlargest(limit)
    client_totals = client_totals.index.tolist()
    client_totals = [str(client) for client in client_totals]
    logger.info(f"Top clients: {client_totals}")
    return client_totals


def get_client_service_level(
    month: Optional[int] = None, client_list: List[str] = [], year: Optional[int] = None
) -> Dict[str, float]:
    """
    Calculate service level (shipped/ordered) for given clients.

    Args:
        month (int): Month to filter, if 0, no filter
        client_list (List[str]): List of client references
        year (int): Year to filter

    Returns:
        Dict[str, float]: Service levels for each client
    """
    df = expeditions_data_sql()
    if df.empty:
        return {}

    # Apply filters
    if year:
        df = df[df["Date"].dt.year == year]  # type: ignore
    if month:
        df = df[df["Date"].dt.month == month]  # type: ignore

    df = df[df["Client"].isin(client_list)]
    if df.empty:
        return {}

    service_levels = {}
    for client in client_list:
        client_data = df[df["Client"] == client]
        total_ordered = client_data["Purchased"].sum()
        total_shipped = client_data["Served"].sum()

        service_level = total_shipped / total_ordered if total_ordered > 0 else 0
        service_levels[client] = round(service_level, 3)

    service_levels = {str(k): float(v) for k, v in service_levels.items()}
    logger.info(f"Calculated service levels for clients: {service_levels}")
    return service_levels


def get_expedition_metrics(
    month: Optional[int] = None,
    client_list: List[str] = [],
    year: Optional[int] = None,
) -> Dict[str, dict]:
    """
    Return count of expeditions, total ordered, total shipped for given clients.

    Args:
        month (int): Month to filter, if 0, no filter
        client_list (List[str]): List of client names
        year (int): Year to filter


    Returns:
        Dict[str, dict]: Metrics for each client
    """
    df = expeditions_data_sql()
    if df.empty:
        return {}

    # Apply filters
    if year:
        df = df[df["Date"].dt.year == year]  # type: ignore
    if month:
        df = df[df["Date"].dt.month == month]  # type: ignore

    df = df[df["Client"].isin(client_list)]
    if df.empty:
        return {}

    metrics = {}
    for client in client_list:
        client_data = df[df["Client"] == client]
        metrics[client] = {
            "expedition_count": int(len(client_data)),
            "total_ordered": float(client_data["Purchased"].sum()),
            "total_shipped": float(client_data["Served"].sum()),
        }
    logger.info(f"Calculated expedition metrics for clients: {metrics}")
    return metrics
