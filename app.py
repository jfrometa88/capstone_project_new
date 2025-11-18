table_style = {
    'width': '100%',
    'borderCollapse': 'collapse',
    'border': '1px solid #bdc3c7',
    'fontFamily': 'Arial, sans-serif',
    'fontSize': '14px',
    'boxShadow': '0 2px 3px rgba(0,0,0,0.1)',
    'borderRadius': '8px',
    'overflow': 'hidden'
}

table_header_style = {
    'backgroundColor': '#34495e',
    'color': 'white',
    'padding': '12px 15px',
    'textAlign': 'center',
    'fontWeight': 'bold',
    'border': '1px solid #2c3e50',
    'fontSize': '14px'
}

table_cell_style = {
    'padding': '10px 12px',
    'border': '1px solid #bdc3c7',
    'textAlign': 'center',
    'backgroundColor': 'white'
}

import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger()

# Import our utility functions
from utils.data_loader import load_expeditions_data, load_stock_data
from utils.expedition_analysis import get_top_clients, get_client_service_level, get_expedition_metrics
from utils.reference_analysis import get_top_references_expeditions, get_reference_time_series, forecast_next_month_demand
from utils.stock_analysis import get_top_references_stock, get_avg_time_in_warehouse, get_stock_metrics

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Warehouse Analytics Dashboard"

# Load data
expeditions_df = load_expeditions_data()
stock_df = load_stock_data()

# Get available years and months from data
available_years = sorted(expeditions_df['fechaTransporte'].dt.year.unique()) if not expeditions_df.empty else []
available_months = sorted(expeditions_df['fechaTransporte'].dt.month.unique()) if not expeditions_df.empty else []

app.layout = html.Div([
    html.H1("Warehouse Analytics Dashboard", style={'textAlign': 'center', 'marginBottom': 30}),
    
    # Global Filters
    html.Div([
        html.Div([
            html.Label("Select Year:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='year-filter',
                options=[{'label': str(year), 'value': year} for year in available_years],
                value=available_years[-1] if available_years else None,
                clearable=True,
                placeholder="All Years"
            )
        ], style={'width': '23%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            html.Label("Select Month:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='month-filter',
                options=[{'label': datetime(2024, month, 1).strftime('%B'), 'value': month} for month in available_months],
                value=None,
                clearable=True,
                placeholder="All Months"
            )
        ], style={'width': '23%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            html.Label("Number of Clients:", style={'fontWeight': 'bold'}),
            dcc.Slider(
                id='client-slider',
                min=1,
                max=8,
                step=1,
                value=5,
                marks={i: str(i) for i in range(1, 9)}
            )
        ], style={'width': '27%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            html.Label("Number of References:", style={'fontWeight': 'bold'}),
            dcc.Slider(
                id='reference-slider',
                min=1,
                max=8,
                step=1,
                value=5,
                marks={i: str(i) for i in range(1, 9)}
            )
        ], style={'width': '27%', 'display': 'inline-block', 'padding': '10px'})
    ], style={'backgroundColor': '#f9f9f9', 'padding': '15px', 'borderRadius': '10px', 'marginBottom': '20px'}),
    
    # Tabs
    dcc.Tabs(id='tabs', value='tab1', children=[
        dcc.Tab(label='📊 Client Service Level', value='tab1'),
        dcc.Tab(label='🚚 Reference Importance (Expeditions)', value='tab2'),
        dcc.Tab(label='📦 Reference Importance (Stock)', value='tab3'),
    ]),
    
    html.Div(id='tabs-content', style={'padding': '20px'})
])

# Tab content callback
@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value'),
     Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('client-slider', 'value'),
     Input('reference-slider', 'value')]
)
def render_tab_content(tab, year, month, client_limit, reference_limit):
    if tab == 'tab1':
        return render_client_service_tab(year, month, client_limit)
    elif tab == 'tab2':
        return render_reference_expeditions_tab(year, month, reference_limit)
    elif tab == 'tab3':
        return render_reference_stock_tab(reference_limit)

def render_client_service_tab(year, month, client_limit):
    """Render content for Client Service Level tab"""
    
    # Get top clients
    top_clients = get_top_clients(limit=client_limit, year=year, month=month)
    
    if not top_clients:
        return html.Div([
            html.H3("Client Service Level Analysis"),
            html.P("No data available for the selected filters.", style={'color': 'red'})
        ])
    
    # Get service levels and metrics
    service_levels = get_client_service_level(top_clients, year, month)
    expedition_metrics = get_expedition_metrics(top_clients, year, month)
    
    # Create service level chart
    fig_service = go.Figure()
    
    clients = list(service_levels.keys())
    levels = list(service_levels.values())
    
    fig_service.add_trace(go.Bar(
        x=clients,
        y=levels,
        name='Service Level',
        marker_color='lightblue'
    ))
    
    # Add mean line
    mean_level = sum(levels) / len(levels) if levels else 0
    fig_service.add_hline(
        y=mean_level, 
        line_dash="dash", 
        line_color="red",
        annotation_text=f"Mean: {mean_level:.3f}"
    )
    
    fig_service.update_layout(
        title='Service Level by Client (Shipped/Ordered)',
        xaxis_title='Client',
        yaxis_title='Service Level Ratio',
        showlegend=False,
        height=400
    )
    
    # Create expedition metrics chart
    ordered = [expedition_metrics[client]['total_ordered'] for client in top_clients]
    shipped = [expedition_metrics[client]['total_shipped'] for client in top_clients]
    
    fig_quantities = go.Figure()
    fig_quantities.add_trace(go.Bar(name='Ordered', x=top_clients, y=ordered, marker_color='orange'))
    fig_quantities.add_trace(go.Bar(name='Shipped', x=top_clients, y=shipped, marker_color='green'))
    
    fig_quantities.update_layout(
        title='Total Quantities: Ordered vs Shipped',
        xaxis_title='Client',
        yaxis_title='Quantity',
        barmode='group',
        height=400
    )
    
    return html.Div([
        html.H3(f"📊 Client Service Level Analysis - Top {client_limit} Clients"),
        
        html.Div([
            html.Div([
                dcc.Graph(figure=fig_service)
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            html.Div([
                dcc.Graph(figure=fig_quantities)
            ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
        ]),
        
        html.Hr(),
        html.H4("Detailed Metrics"),
        html.Table([
            html.Thead([
                html.Tr([html.Th("Client", style=table_header_style), 
                         html.Th("Expeditions", style=table_header_style), 
                         html.Th("Total Ordered", style=table_header_style), 
                         html.Th("Total Shipped", style=table_header_style), 
                         html.Th("Service Level", style=table_header_style)])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td(client, style=table_cell_style),
                    html.Td(expedition_metrics[client]['expedition_count'], style=table_cell_style),
                    html.Td(f"{expedition_metrics[client]['total_ordered']:,.0f}", style=table_cell_style),
                    html.Td(f"{expedition_metrics[client]['total_shipped']:,.0f}", style=table_cell_style),
                    html.Td(f"{service_levels[client]:.3f}", style=table_cell_style)
                ]) for client in top_clients
            ])
        ], style=table_style)
    ])

def render_reference_expeditions_tab(year, month, reference_limit):
    """Render content for Reference Importance (Expeditions) tab"""
    
    # Get top references
    top_references = get_top_references_expeditions(limit=reference_limit, year=year, month=month)
    
    if not top_references:
        return html.Div([
            html.H3("Reference Importance in Expeditions"),
            html.P("No data available for the selected filters.", style={'color': 'red'})
        ])
    
    # Get time series data and forecasts
    time_series = get_reference_time_series(top_references, year, month)
    forecasts = forecast_next_month_demand(top_references)
    
    # Create time series chart
    fig_time_series = go.Figure()
    
    for ref in top_references:
        if ref in time_series and time_series[ref]['dates']:
            fig_time_series.add_trace(go.Scatter(
                x=time_series[ref]['dates'],
                y=time_series[ref]['quantities'],
                mode='lines+markers',
                name=f'Reference {ref}'
            ))
    
    fig_time_series.update_layout(
        title='Time Series of Shipped Quantity by Reference',
        xaxis_title='Month',
        yaxis_title='Shipped Quantity',
        height=400
    )
    
    # Create forecast chart
    fig_forecast = go.Figure()
    
    ref_names = [f'Ref {ref}' for ref in top_references]
    forecast_values = [forecasts.get(ref, 0) for ref in top_references]
    
    fig_forecast.add_trace(go.Bar(
        x=ref_names,
        y=forecast_values,
        marker_color='lightgreen',
        name='Forecasted Demand'
    ))
    
    fig_forecast.update_layout(
        title='Next Month Demand Forecast',
        xaxis_title='Reference',
        yaxis_title='Forecasted Quantity',
        height=400
    )
    
    return html.Div([
        html.H3(f"🚚 Reference Importance in Expeditions - Top {reference_limit} References"),
        
        html.Div([
            html.Div([
                dcc.Graph(figure=fig_time_series)
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            html.Div([
                dcc.Graph(figure=fig_forecast)
            ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
        ]),
        
        html.Hr(),
        html.H4("Demand Forecast Details"),
        html.Table([
            html.Thead([
                html.Tr([html.Th("Reference ID", style=table_header_style), 
                         html.Th("Next Month Forecast", style=table_header_style)])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td(f"Reference {ref}", style=table_cell_style),
                    html.Td(f"{forecasts.get(ref, 0):,.0f}", style=table_cell_style)
                ]) for ref in top_references
            ])
        ], style=table_style)
    ])

def render_reference_stock_tab(reference_limit):
    """Render content for Reference Importance (Stock) tab"""
    
    # Get top references from stock
    top_references = get_top_references_stock(limit=reference_limit)
    
    if not top_references:
        return html.Div([
            html.H3("Reference Importance in Stock Locations"),
            html.P("No stock data available.", style={'color': 'red'})
        ])
    
    # Get stock metrics and average times
    stock_metrics = get_stock_metrics(top_references)
    avg_times = get_avg_time_in_warehouse(top_references)
    
    # Create stock quantity chart
    quantities = [stock_metrics[ref]['total_pieces'] for ref in top_references]
    
    fig_quantities = go.Figure()
    fig_quantities.add_trace(go.Bar(
        x=top_references,
        y=quantities,
        marker_color='lightcoral',
        name='Total Pieces'
    ))
    
    fig_quantities.update_layout(
        title='Total Pieces in Stock by Reference',
        xaxis_title='Reference',
        yaxis_title='Total Pieces',
        height=400
    )
    
    # Create average time chart
    times = [avg_times.get(ref, 0) for ref in top_references]
    
    fig_times = go.Figure()
    fig_times.add_trace(go.Bar(
        x=top_references,
        y=times,
        marker_color='darkslateblue',
        name='Avg Time in Warehouse (days)'
    ))
    
    fig_times.update_layout(
        title='Average Time in Warehouse by Reference',
        xaxis_title='Reference',
        yaxis_title='Average Days',
        height=400
    )
    
    return html.Div([
        html.H3(f"📦 Reference Importance in Stock - Top {reference_limit} References"),
        
        html.Div([
            html.Div([
                dcc.Graph(figure=fig_quantities)
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            html.Div([
                dcc.Graph(figure=fig_times)
            ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
        ]),
        
        html.Hr(),
        html.H4("Stock Metrics Details"),
        html.Table([
            html.Thead([
                html.Tr([html.Th("Reference", style=table_header_style), 
                         html.Th("Total Pieces", style=table_header_style), 
                         html.Th("Locations", style=table_header_style), 
                         html.Th("HUs", style=table_header_style), 
                         html.Th("Avg Time (days)", style=table_header_style)])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td(ref, style=table_cell_style),
                    html.Td(f"{stock_metrics[ref]['total_pieces']:,.0f}", style=table_cell_style),
                    html.Td(stock_metrics[ref]['location_count'], style=table_cell_style),
                    html.Td(stock_metrics[ref]['hu_count'], style=table_cell_style),
                    html.Td(f"{avg_times.get(ref, 0):.1f}", style=table_cell_style)
                ]) for ref in top_references
            ])
        ], style=table_style)
    ])

if __name__ == '__main__':
    app.run(debug=True)