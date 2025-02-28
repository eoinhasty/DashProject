import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input
import plotly.express as px
import pandas as pd

# Load your pre-processed master data
master_df = pd.read_csv('data/master_cleaned.csv', parse_dates=['transfer_date', 'date_of_birth'])
master_df['transfer_year'] = master_df['transfer_date'].dt.year

# Example figure: max transfer fee per year
max_fee_per_year = master_df.groupby('transfer_year')['transfer_fee'].max().reset_index()
fig_bar = px.bar(max_fee_per_year, x='transfer_year', y='transfer_fee', title='Max Transfer Fee per Year')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Tabs([
        dbc.Tab(label="Time Based", tab_id="tab-time"),
        dbc.Tab(label="Leagues", tab_id="tab-leagues"),
        dbc.Tab(label="Clubs", tab_id="tab-clubs"),
        dbc.Tab(label="Players", tab_id="tab-players"),
    ], id="tabs", active_tab="tab-time"),
    html.Div(id="tab-content")
])

@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab")
)
def render_tab_content(active_tab):
    if active_tab == "tab-time":
        return dbc.Container([
            # Add your interactive components, like sliders and charts for the Time Based tab
            dcc.Graph(figure=fig_bar)
        ])
    elif active_tab == "tab-leagues":
        return dbc.Container([
            # Charts and filters for Leagues tab
            html.Div("Leagues tab content")
        ])
    elif active_tab == "tab-clubs":
        return dbc.Container([
            # Charts and filters for Clubs tab
            html.Div("Clubs tab content")
        ])
    elif active_tab == "tab-players":
        return dbc.Container([
            # Charts and filters for Players tab
            html.Div("Players tab content")
        ])
    return "No tab selected"

if __name__ == '__main__':
    app.run_server(debug=True)
