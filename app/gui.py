import dash
from dash import html, Input, Output
import dash_bootstrap_components as dbc
import dash_leaflet as dl
from database import db

header = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand("EV_Central Monitor", className="ms-2", style={"color": "white"}),
        dbc.Input(id="search-input", placeholder="Buscar punto de recarga...", type="search", style={"width": "300px"}),
    ]),
    color="primary",
    dark=True,
    fixed="top"
)

def cp_widget(id: str, state: str) -> html.Div:
    return html.Div([
        html.H3(id),
        html.P(f"Estado: {state}")
    ], className="cp")

cps = db.get_cps()

points = []
for cp in cps:
    points.append(
        {
            "id": cp[0],
            "location": [cp[1], cp[2]],
            "name": cp[3]
        }
    )


widgets = []
for cp in cps:
    widgets.append(cp_widget(cp[0], cp[5]))

sidebar = html.Aside([
    html.H5("Menú", className="display-6"),
    html.Hr(),
    html.P("Aquí se añadirán elementos futuros", className="lead"),
    *widgets
])

markers = [dl.Marker(position=pt["location"], children=dl.Tooltip(pt["name"])) for pt in points]

mapa = dl.Map(center=[40.4168, -3.7038], zoom=13, children=[
    dl.TileLayer(),
    dl.LayerGroup(markers)
], style={"width": "100%", "height": "600px"})

content = html.Div([
    html.H3("Mapa de Puntos de Recarga"),
    mapa,
], id="content")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], assets_folder="assets")

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
