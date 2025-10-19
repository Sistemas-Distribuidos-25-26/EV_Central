import dash
from dash import html, Input, Output, State, dcc
import dash_bootstrap_components as dbc
import dash_leaflet as dl
from database import db
from flask import Flask
import logging

server = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

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

def req_widget(timestamp: str, driver: str, cp: str) -> html.Tr:
    return html.Tr([
        html.Td(timestamp),
        html.Td(driver),
        html.Td(cp)
    ])

points = []
for cp in db.get_cps():
    points.append(
        {
            "id": cp[0],
            "location": [cp[1], cp[2]],
            "name": cp[3]
        }
    )

def reload_cps(query: str):
    widgets = []
    cps = db.get_cps()
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

def reload_requests():
    request_widgets : list[html.Tr] = []
    requests = db.get_requests()
    for rq in requests:
        request_widgets.append(req_widget(rq[0],rq[1],rq[2]))
    return request_widgets

# Primera carga de información con la info guardada en la DB
reload_requests()
reload_cps("")

sidebar = html.Aside([
    html.H5("Menú", className="display-6"),
    html.Hr(),
    html.Div([], id="widget-sidebar")
], id="widget-panel")

markers = [dl.Marker(position=pt["location"], children=dl.Tooltip(pt["name"])) for pt in points]

mapa = dl.Map(center=[40.4168, -3.7038], zoom=13, children=[
    dl.TileLayer(),
    dl.LayerGroup(markers)
], style={"width": "50%", "height": "800px"}, id="map")

control_panel = html.Aside([
    html.P("Peticiones en curso"),
    html.Table([
        html.Thead([
            html.Tr([html.Th("Timestamp"), html.Th("DriverID"), html.Th("CP")])
        ]),
        html.Tbody(
            [], id="requests-sidebar"
        )]),
    html.P("Mensajes internos"),
    html.Pre("")
], id="control-panel")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], assets_folder="assets", server=server, update_title="Updating...")

app.layout = html.Div([
    header,
    sidebar,
    mapa,
    control_panel,
    dcc.Interval(interval=1000, n_intervals=0, id="interval_component")
])

@app.callback(
    [Output("widget-sidebar", "children"),
     Output("requests-sidebar", "children")],
    Input("interval_component", "n_intervals"),
    State("search-input", "value")
)
def refresh(n, value):
    cps = reload_cps(value)
    requests = reload_requests()
    return cps, requests


def run():
    app.run(host="0.0.0.0", port=10001)
