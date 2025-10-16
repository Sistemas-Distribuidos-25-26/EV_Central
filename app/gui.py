import dash
from dash import html, Input, Output, dcc
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

COLOR_MAP = {
    "UNKNOWN": "#b0a7b8",
    "ACTIVE": "#9de64e",
    "OUT_OF_ORDER": "#de5d3a",
    "CHARGING":"#3388de",
    "BROKEN": "#ec273f",
    "DISCONNECTED": "#b0a7b8"
}

def cp_widget(id: str, state: str, price: str) -> html.Div:
    return html.Div([
        html.H3(id),
        html.P(f"Estado: {state}"),
        html.P(f"{price}€/kWh")
    ], className="cp", style={"background-color": COLOR_MAP.get(state, "white")})

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
    widgets.append(cp_widget(cp[0], cp[5], cp[4]))

sidebar = html.Aside([
    html.H5("Menú", className="display-6"),
    html.Hr(),
    html.Div([*widgets], id="widget-sidebar")
], id="widget-panel")

markers = [dl.Marker(position=pt["location"], children=dl.Tooltip(pt["name"])) for pt in points]

mapa = dl.Map(center=[40.4168, -3.7038], zoom=13, children=[
    dl.TileLayer(),
    dl.LayerGroup(markers)
], style={"width": "70%", "height": "800px"}, id="map")

control_panel = html.Aside([
    html.P("Peticiones en curso"),
    html.P("Mensajes internos"),
    html.Pre("")
], id="control-panel")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], assets_folder="assets")

app.layout = html.Div([
    header,
    sidebar,
    mapa,
    control_panel,
    dcc.Interval(interval=1000, id="interval-component", n_intervals=0)
])

@app.callback(
    Output("widget-sidebar", "children"),
    Input("interval-component", "n_intervals")
)
def refresh_cps(n):
    global widgets
    global cps
    widgets = []
    cps = db.get_cps()
    for cp in cps:
        widgets.append(cp_widget(cp[0], cp[5], cp[4]))
    return widgets


@app.callback(
    Output("widget-sidebar", "children"),
    [Input("search-input", "value")]
)
def search_ev_points(query: str):
    global widgets
    print(f"Búsqueda: {query}")

    widgets = []
    if query == "" or query is None:
        for cp in cps:
            widgets.append(cp_widget(cp[0], cp[5], cp[4]))
    else:
        for cp in cps:
            if str(cp[0]).find(query.upper()) != -1:
                widgets.append(cp_widget(cp[0], cp[5], cp[4]))
    if not widgets:
        widgets = [html.P("No hay resultados")]
    return widgets

def run():
    app.run()
