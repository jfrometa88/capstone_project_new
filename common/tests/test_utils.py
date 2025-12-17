import os
import sys
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))

project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from common.utils import data_loader


def test_load_expeditions_data():
    df = data_loader.load_expeditions_data()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    expected_columns = {"Date", "Client", "Purchased", "Served"}
    assert expected_columns.issubset(set(df.columns))


def test_load_stock_data():
    df = data_loader.load_stock_data()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    expected_columns = {"Location", "Material", "HU", "Stock", "Date"}
    assert expected_columns.issubset(set(df.columns))


def test_get_top_clients():
    from common.utils.expedition_analysis import get_top_clients

    top_clients = get_top_clients(limit=3, year=2025, month=1)
    assert isinstance(top_clients, list)
    assert len(top_clients) <= 3
    for client in top_clients:
        assert isinstance(client, str)


def test_get_client_service_level():
    from common.utils.expedition_analysis import get_client_service_level

    client_list = ["88977875", "6828"]
    service_levels = get_client_service_level(
        month=2,
        client_list=client_list,
        year=2025,
    )
    assert isinstance(service_levels, dict)
    for client in client_list:
        assert client in service_levels
        assert isinstance(service_levels[client], float)
        assert 0.0 <= service_levels[client] <= 1.0


def test_get_expedition_metrics():
    from common.utils.expedition_analysis import get_expedition_metrics

    client_list = ["88977875", "6828"]
    metrics = get_expedition_metrics(
        month=2,
        client_list=client_list,
        year=2025,
    )
    assert isinstance(metrics, dict)
    for client in client_list:
        assert client in metrics
        assert isinstance(metrics[client], dict)
        assert "expedition_count" in metrics[client]
        assert "total_ordered" in metrics[client]
        assert "total_shipped" in metrics[client]
        assert isinstance(metrics[client]["expedition_count"], int)
        assert isinstance(metrics[client]["total_ordered"], (int, float))
        assert isinstance(metrics[client]["total_shipped"], (int, float))
