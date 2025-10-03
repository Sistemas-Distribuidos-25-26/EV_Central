import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import dash_leaflet as dl

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": "56px",
    "left": 0,
    "bottom": 0,
    "width": "250px",
    "padding": "1rem",
    "background-color": "#f8f9fa",
    "overflowY": "auto",
}

CONTENT_STYLE = {
    "margin-left": "260px",
    "margin-top": "56px",
    "padding": "1rem",
}

header = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand("EV_Central Monitor", className="ms-2", style={"color": "white"}),
        dbc.Input(id="search-input", placeholder="Buscar punto de recarga...", type="search", style={"width": "300px"}),
    ]),
    color="primary",
    dark=True,
    fixed="top",
    style={"height": "56px"},
)

sidebar = html.Div([
    html.H5("Menú", className="display-6"),
    html.Hr(),
    html.P("Aquí se añadirán elementos futuros", className="lead"),
], style=SIDEBAR_STYLE)

points = [
    {"id": "CP001", "location": [40.4168, -3.7038], "name": "Estación Centro"},
    {"id": "CP002", "location": [40.4239, -3.6911], "name": "Estación Norte"},
    {"id": "CP003", "location": [40.4098, -3.7104], "name": "Estación Sur"},
]

markers = [dl.Marker(position=pt["location"], children=dl.Tooltip(pt["name"])) for pt in points]

mapa = dl.Map(center=[40.4168, -3.7038], zoom=13, children=[
    dl.TileLayer(),
    dl.LayerGroup(markers)
], style={"width": "100%", "height": "600px"})

content = html.Div([
    html.H3("Mapa de Puntos de Recarga"),
    mapa,
], style=CONTENT_STYLE)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    header,
    sidebar,
    content,
])

@app.callback(
    Output("search-input", "value"),
    Input("search-input", "value"),
)
def search_ev_points(query):
    if query:
        print(f"Búsqueda: {query}")
    return dash.no_update

def run():
    app.run()
