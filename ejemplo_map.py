import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from common.utils.logger import setup_logger

logger = setup_logger('dash_app.app')


# 1. Preparación de datos (Simulamos una base de datos de tanques/estaciones)
# En una app real, estos datos vendrían de tu SQL Server o SQLite
data = {
    'Nombre': ['Tanque Central', 'Planta Norte', 'Depósito Sur', 'Puerto Este'],
    'Latitud': [39.4697, 39.4850, 39.4500, 39.4600],
    'Longitud': [-0.3774, -0.3900, -0.3600, -0.3300],
    'Nivel': [85, 42, 15, 98] # Porcentaje de llenado
}
df = pd.DataFrame(data)

# 2. Inicializar la aplicación Dash
app = dash.Dash(__name__)

# 3. Definir el diseño (Layout)
app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'padding': '20px'}, children=[
    html.H1("Monitor de Geoposicionamiento (OSM)", style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    html.Div([
        html.P("Selecciona el nivel mínimo de carga a visualizar:"),
        dcc.Slider(
            id='nivel-slider',
            min=0, max=100, step=10,
            value=0,
            marks={i: f'{i}%' for i in range(0, 101, 20)}
        ),
    ], style={'marginBottom': '30px', 'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px'}),

    # Contenedor del mapa
    dcc.Graph(id='mapa-interactivo', style={'height': '70vh'})
])

# 4. Callback para actualizar el mapa según el Slider
@app.callback(
    Output('mapa-interactivo', 'figure'),
    [Input('nivel-slider', 'value')]
)
def update_map(nivel_minimo):
    # Filtrar datos según la interacción del usuario
    df_filtrado = df[df['Nivel'] >= nivel_minimo]
    
    # Crear el mapa usando Plotly Express
    # 'open-street-map' es el estilo gratuito que no requiere API Key (como Google Maps)
    fig = px.scatter_map(
        df_filtrado,
        lat="Latitud",
        lon="Longitud",
        hover_name="Nombre",
        hover_data={"Nivel": True, "Latitud": False, "Longitud": False},
        color="Nivel",
        color_continuous_scale=px.colors.sequential.Viridis,
        size_max=15,
        zoom=11
    )

    # Configurar el diseño del mapa para usar OpenStreetMap
    fig.update_layout(
        mapbox_style="open-street-map", 
        margin={"r":0,"t":0,"l":0,"b":0},
        hovermode='closest'
    )
    
    return fig

# 5. Ejecutar el servidor
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8025, debug=True)