# [Nombre del programa, ej: Warehouse AI Agent]
# Copyright (C) [Año] [Tu Nombre Completo]
# 
# Este programa es software libre: usted puede redistribuirlo y/o modificarlo
# bajo los términos de la Licencia Pública General de GNU
# tal como la publica la Free Software Foundation, ya sea la versión 3
# de la Licencia, o (a su elección) cualquier versión posterior.
#
# Este programa se distribuye con la esperanza de que sea útil,
# pero SIN NINGUNA GARANTÍA; incluso sin la garantía implícita de
# COMERCIALIZACIÓN o IDONEIDAD PARA UN PROPÓSITO PARTICULAR. 
# Consulte la Licencia Pública General de GNU para más detalles.
#
# Debería haber recibido una copia de la Licencia Pública General de GNU
# junto con este programa. Si no, vea <https://www.gnu.org/licenses/>.

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
from dash import dcc, html, Input, Output, callback, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import requests

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
    
    # ai_chat_section
    html.Div([
        html.Div([
            html.H3("🤖 AI Warehouse Assistant", 
                    style={'color': '#2c3e50', 'marginBottom': '15px', 'display': 'inline-block'}),
            html.Span("Powered by Gemini", 
                    style={'float': 'right', 'backgroundColor': '#4285f4', 'color': 'white', 
                        'padding': '5px 10px', 'borderRadius': '12px', 'fontSize': '12px',
                        'marginTop': '8px'})
        ]),

        html.Div(id='server-status', style={'marginBottom': '10px', 'fontSize': '12px'}),
        
        html.Div([
            dcc.Textarea(
                id='ai-chat-input',
                placeholder='💡 Ask me anything about:\n• Client service levels\n• Stock analysis  \n• Demand forecasting\n• Inventory optimization...',
                style={
                    'width': '100%', 
                    'height': '80px', 
                    'marginBottom': '10px',
                    'padding': '12px',
                    'border': '2px solid #e1e8ed',
                    'borderRadius': '8px',
                    'fontSize': '14px',
                    'resize': 'vertical'
                }
            ),
            html.Div([
                html.Button('🚀 Ask AI Assistant', id='ai-chat-button', n_clicks=0,
                        style={
                            'backgroundColor': '#3498db', 
                            'color': 'white', 
                            'border': 'none', 
                            'padding': '12px 24px', 
                            'borderRadius': '6px', 
                            'cursor': 'pointer',
                            'fontSize': '14px',
                            'fontWeight': 'bold'
                        }),
                html.Div(id='chat-loading', style={'display': 'inline-block', 'marginLeft': '10px'})
            ]),
        ]),
        
        html.Div(id='ai-chat-response', style={
            'marginTop': '20px', 
            'padding': '20px', 
            'backgroundColor': '#f8f9fa', 
            'borderRadius': '10px',
            'border': '1px solid #dfe6e9',
            'minHeight': '120px',
            'whiteSpace': 'pre-wrap',
            'lineHeight': '1.6'
        }),
        
        html.Div([
            html.P("💡 Example questions:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'color': '#2c3e50'}),
            html.Div([
                html.Button("Show top clients", id="example-1", n_clicks=0,
                        style={'margin': '2px', 'padding': '5px 10px', 'fontSize': '12px', 
                                'border': '1px solid #bdc3c7', 'borderRadius': '4px', 
                                'backgroundColor': '#ecf0f1', 'cursor': 'pointer'}),
                html.Button("Analyze stock aging", id="example-2", n_clicks=0,
                        style={'margin': '2px', 'padding': '5px 10px', 'fontSize': '12px', 
                                'border': '1px solid #bdc3c7', 'borderRadius': '4px', 
                                'backgroundColor': '#ecf0f1', 'cursor': 'pointer'}),
                html.Button("Forecast demand", id="example-3", n_clicks=0,
                        style={'margin': '2px', 'padding': '5px 10px', 'fontSize': '12px', 
                                'border': '1px solid #bdc3c7', 'borderRadius': '4px', 
                                'backgroundColor': '#ecf0f1', 'cursor': 'pointer'}),
                html.Button("Service level report", id="example-4", n_clicks=0,
                        style={'margin': '2px', 'padding': '5px 10px', 'fontSize': '12px', 
                                'border': '1px solid #bdc3c7', 'borderRadius': '4px', 
                                'backgroundColor': '#ecf0f1', 'cursor': 'pointer'}),
            ])
        ], style={'marginTop': '15px', 'fontSize': '13px'})
    ], style={
        'padding': '25px', 
        'backgroundColor': 'white', 
        'borderRadius': '12px', 
        'marginBottom': '25px', 
        'border': '1px solid #ecf0f1',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
    }),

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
    service_levels = get_client_service_level(month=month, client_list=top_clients, year=year)
    expedition_metrics = get_expedition_metrics(month=month, client_list=top_clients, year=year)
    
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
    time_series = get_reference_time_series(month=month, reference_list=top_references, year=year)
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

# Callbacks for AI chat functionality
@callback(
    Output('ai-chat-input', 'value'),
    [Input('example-1', 'n_clicks'),
     Input('example-2', 'n_clicks'),
     Input('example-3', 'n_clicks'),
     Input('example-4', 'n_clicks')]
)
def update_chat_input(example1, example2, example3, example4):
    ctx = dash.callback_context
    if not ctx.triggered:
        return ""
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    examples = {
        'example-1': "Show me the top 5 clients and their service levels for this year in month 1",
        'example-2': "Analyze inventory aging for our top 5 stock references",
        'example-3': "Forecast next month demand for our most shipped references", 
        'example-4': "Generate a comprehensive service level report for all clients"
    }
    
    return examples.get(button_id, "")

# Callback to show loading
@callback(
    Output('chat-loading', 'children'),
    [Input('ai-chat-button', 'n_clicks')],
    [State('ai-chat-input', 'value')]
)
def show_loading(n_clicks, message):
    if n_clicks > 0 and message:
        return "⏳ Processing..."
    return ""

@callback(
    Output('ai-chat-response', 'children'),
    [Input('ai-chat-button', 'n_clicks')],
    [State('ai-chat-input', 'value')],
    prevent_initial_call=True
)
def update_ai_chat(n_clicks, user_message):
    if not user_message or user_message.strip() == "":
        return html.Div([
            html.P("Please enter a question to get AI-powered insights.", 
                   style={'color': '#7f8c8d', 'fontStyle': 'italic'})
        ])
    
    try:
        query = {"message": user_message, "session_id": "user_id_from_dash"}
        response = requests.post(
        "http://localhost:8000/query",
        json=query
    )
        
        return html.Div([
            html.P("🤖 AI Assistant:", 
                   style={'fontWeight': 'bold', 'marginBottom': '10px', 'color': '#2c3e50'}),
            html.Div(response.json().get('response', 'No response received.'),
                    style={
                        'lineHeight': '1.6', 
                        'padding': '15px', 
                        'backgroundColor': 'white', 
                        'borderRadius': '8px',
                        'border': '1px solid #e1e8ed'
                    })
        ])
        
    except Exception as e:
        logger.error(f"Error in AI chat callback: {e}")
        return html.Div([
            html.P("❌ Error:", 
                   style={'fontWeight': 'bold', 'color': '#e74c3c', 'marginBottom': '10px'}),
            html.P(f"Failed to get AI response: {str(e)}", 
                   style={'color': '#7f8c8d'}),
            html.P("Please check if the AI service is properly configured.", 
                   style={'color': '#7f8c8d', 'fontStyle': 'italic'})
        ])

# Callback to show loading
@callback(
    Output('ai-chat-response', 'children', allow_duplicate=True),
    [Input('ai-chat-button', 'n_clicks')],
    [State('ai-chat-input', 'value')],
    prevent_initial_call=True
)
def show_loading(n_clicks, user_message):
    if n_clicks and user_message:
        return html.Div([
            html.Div([
                html.Span("⏳ Processing your query...", 
                         style={'marginLeft': '10px', 'color': '#3498db'})
            ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 
                     'padding': '20px'})
        ])
    return dash.no_update

@callback(
    Output('server-status', 'children'),
    [Input('tabs', 'value')]
)
def update_server_status(tab):
    if tab == 'tab1':
        is_healthy = requests.get(
            "http://localhost:8000/health",
            timeout=30
        )
        
        if is_healthy.status_code == 200:
            return html.Span("🟢 Agent Server Connected", 
                            style={'color': 'green', 'fontSize': '12px'})
        else:
            return html.Span("🔴 Agent Server Offline", 
                            style={'color': 'red', 'fontSize': '12px'})

if __name__ == '__main__':
    app.run(debug=True)