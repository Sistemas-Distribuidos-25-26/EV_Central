import dash
from dash import html, Input, Output, State, dcc, ALL
import dash_bootstrap_components as dbc
import dash_leaflet as dl
from database import db
from flask import Flask
import logging
import config
from kafka_producer import change_state

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
    "DESCONECTADO": "#b0a7b8",
    "ACTIVO": "#9de64e",
    "FUERA DE SERVICIO": "#de5d3a",
    "SUMINISTRANDO":"#3388de",
    "K.O.": "#ec273f",
    "AVERIADO": "#ec273f"
}

def cp_widget(id: str, state: str, price: str, paired: str | None, total_charged: str | None) -> html.Div:
    return html.Div([
        html.H3(id),
        html.P(f"Estado: {state}"),
        html.P(f"{price}€/kWh"),
        html.Div([
            html.P(f"{paired}"),
            html.P(f"{total_charged}kWh")
        ]) if paired and total_charged else None
    ], className="cp", id={"type":"cp-widget", "index": id}, n_clicks=0 ,style={"background-color": COLOR_MAP.get(state, "white")})

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
            widgets.append(cp_widget(cp[0], cp[5], cp[4], cp[6], cp[7] if cp[7] else "0"))
    else:
        for cp in cps:
            if str(cp[0]).find(query.upper()) != -1:
                widgets.append(cp_widget(cp[0], cp[5], cp[4], cp[6], cp[7] if cp[7] else "0"))
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
    html.Div([
        html.Button("Desactivar todos", id="disable-all-button", n_clicks=0),
        html.Button("Activar todos", id="enable-all-button", n_clicks=0)
    ], id="general-controls"),
    html.Div([], id="widget-sidebar")
], id="widget-panel")

markers = [dl.Marker(position=pt["location"], children=dl.Tooltip(pt["name"])) for pt in points]

mapa = dl.Map(center=[38.5, -0.4038], zoom=9, children=[
    dl.TileLayer(),
    dl.LayerGroup(markers)
], id="map")

control_panel = html.Aside([
    html.H3("Peticiones en curso"),
    html.Hr(),
    html.Table([
        html.Thead([
            html.Tr([html.Th("Timestamp"), html.Th("DriverID"), html.Th("CP")])
        ]),
        html.Tbody(
            [], id="requests-sidebar"
        )]),
    html.H3("Mensajes internos"),
    html.Hr(),
    html.Pre("", id="log_panel")
], id="control-panel")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], assets_folder="assets", server=server, update_title="Updating...")

app.layout = html.Div([
    header,
    sidebar,
    mapa,
    control_panel,
    dcc.Interval(interval=1000, n_intervals=0, id="interval_component")
], id="main_div")

@app.callback(
    [Output("widget-sidebar", "children"),
     Output("requests-sidebar", "children"),
     Output("log_panel", "children")],
    Input("interval_component", "n_intervals"),
    State("search-input", "value")
)
def refresh(n, value):
    cps = reload_cps(value)
    requests = reload_requests()
    config.LOG_FILE.seek(0)
    logs = config.LOG_FILE.read()
    return cps, requests, logs

@app.callback(
    Output("main_div", "children"),
    Input({'type': 'cp-widget', 'index': ALL}, 'n_clicks'),
    State({'type': 'cp-widget', 'index': ALL}, 'id')
)
def on_cp_click(clicks, ids):
    for i, c in enumerate(clicks):
        if c:
            cp_id = ids[i]['index']
            cp_state = db.get_cp(cp_id)[5]
            change_state(cp_id, cp_state == "ACTIVO")
    return dash.no_update

@app.callback(
    Output("disable-all-button", "children"),
    Input("disable-all-button", "n_clicks")
)
def disable_all(n):
    config.log("[Central] Desactivando todos los CP...")
    all_cps = db.get_cps()
    for cp in all_cps:
        change_state(cp[0], True)
    return dash.no_update

@app.callback(
    Output("enable-all-button", "children"),
    Input("enable-all-button", "n_clicks")
)
def enable_all(n):
    config.log("[Central] Activando todos los CP...")
    all_cps = db.get_cps()
    for cp in all_cps:
        change_state(cp[0], False)
    return dash.no_update

def run():
    app.run(host="0.0.0.0", port=10000)
