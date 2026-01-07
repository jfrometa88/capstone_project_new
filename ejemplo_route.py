import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import osmnx as ox
import networkx as nx
import pandas as pd

# 1. Configuración de la Red Vial (se hace una vez al arrancar)
# Descargamos el grafo de calles de una zona (ej: Valencia centro)
config_place = "Valencia, Spain"
# network_type='drive' asegura que la ruta respete sentidos de calles y giros
G = ox.graph_from_place(config_place, network_type='drive')

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Simulador de Ruta entre Tanques", style={'textAlign': 'center'}),
    html.P("Haz clic en el botón para calcular la ruta entre el Tanque A y el Tanque B", style={'textAlign': 'center'}),
    html.Div([
        html.Button("Calcular Viaje Hipotético", id="btn-ruta", n_clicks=0, 
                    style={'padding': '10px', 'fontSize': '16px', 'cursor': 'pointer'})
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),
    
    dcc.Graph(id='mapa-ruta', style={'height': '75vh'})
])

@app.callback(
    Output('mapa-ruta', 'figure'),
    Input('btn-ruta', 'n_clicks')
)
def draw_route(n_clicks):
    # Coordenadas hipotéticas de dos puntos (Tanque A y Tanque B)
    # En una app real, podrías sacarlas de tu base de datos SQLite
    punto_a = (39.4750, -0.3750) # Lat, Lon
    punto_b = (39.4580, -0.3550)

    # Crear el objeto figura base
    fig = go.Figure()

    # Si se ha pulsado el botón, calculamos la ruta real por calle
    if n_clicks > 0:
        # A. Encontrar los nodos más cercanos en la red a nuestras coordenadas
        orig_node = ox.nearest_nodes(G, punto_a[1], punto_a[0])
        dest_node = ox.nearest_nodes(G, punto_b[1], punto_b[0])

        # B. Calcular la ruta más corta (algoritmo Dijkstra)
        route = nx.shortest_path(G, orig_node, dest_node, weight='length')

        # C. Extraer las coordenadas de cada punto de la ruta para graficar
        route_lat = []
        route_lon = []
        for node in route:
            route_lat.append(G.nodes[node]['y'])
            route_lon.append(G.nodes[node]['x'])

        # D. Añadir la línea de la ruta al mapa
        fig.add_trace(go.Scattermap(
            mode = "lines",
            lon = route_lon,
            lat = route_lat,
            line = dict(width = 4, color = 'blue'),
            name = "Ruta de Transporte",
            hoverinfo='none'
        ))

    # Añadir marcadores para los tanques
    fig.add_trace(go.Scattermap(
        mode = "markers+text",
        lon = [punto_a[1], punto_b[1]],
        lat = [punto_a[0], punto_b[0]],
        marker = {'size': 12, 'color': 'red'},
        text = ["Tanque Origen", "Tanque Destino"],
        textposition = "top right"
    ))

    # Configuración de estilo del mapa (OpenStreetMap)
    fig.update_layout(
        mapbox = {
            'style': "open-street-map",
            'center': {'lat': 39.467, 'lon': -0.365},
            'zoom': 13
        },
        margin = {'l':0, 'r':0, 'b':0, 't':0},
        showlegend = False
    )

    return fig

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8030, debug=True)