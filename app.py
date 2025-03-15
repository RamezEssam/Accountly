import pandas as pd
import numpy as np

import plotly.graph_objects as go
import plotly.express as px
import os
import json
import dash
import dash_bootstrap_components as dbc
from datetime import date, timedelta
from dash import Dash, html, dcc, Input, Output, State, MATCH, ALL

from src.layout.navbar import navbar
from src.layout.filters import filters
from src.layout.dashboard import dashboard
from src.layout.about import about

from src.utils.DataConnector import DataConnector

DATA_PATH = ".\\InputForm.xlsm"

data_connector = DataConnector(data_path=DATA_PATH)


app = Dash(
    __name__,
    title="Accountly",
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200",  # Icons
        "https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap",  # Font
    ],
)
server = app.server

app.layout = html.Div(
    [
        dcc.Store(
            id="filters-store",
            data={
                "ExpenseType": [],
                "ExpenseCategory": [],
                "ExpenseDate": [],
            },
        ),
        navbar,
        dbc.Container(
            dbc.Stack(
                [
                    filters,
                    dashboard,
                    about,
                ],
                gap=3,
            ),
            id="content",
            className="p-3",
        ),
    ],
    id="page",
)


# Layout callbacks (collapse, modals, etc)
@app.callback(
    Output("filter-collapse", "is_open"),
    Input("filter-header-btn", "n_clicks"),
    State("filter-collapse", "is_open"),
)
def open_close_filter_collapse(n, current_state):
    if n == 0:
        raise dash.exceptions.PreventUpdate()
    return not current_state


@app.callback(
    Output("filter-header-icon", "children"), Input("filter-collapse", "is_open")
)
def switch_filter_header_icon(is_open):
    if is_open:
        return "keyboard_arrow_up"
    else:
        return "keyboard_arrow_down"


@app.callback(
    Output({"type": "graph-modal", "index": MATCH}, "is_open"),
    Input({"type": "graph-info-btn", "index": MATCH}, "n_clicks"),
)
def show_graph_info_modals(n):
    if n == 0:
        raise dash.exceptions.PreventUpdate()
    return True


@app.callback(Output("about-modal", "is_open"), Input("page-info-btn", "n_clicks"))
def show_about_modal(n):
    if n == 0:
        raise dash.exceptions.PreventUpdate()
    return True


# Filter callbacks (initialization, storing, clearing)
@app.callback(Output("ExpenseCategory", "options"), Input("ExpenseCategory", "id"))
def populate_category_options(_):
    categories = data_connector.get_available_categories()
    return [{"label": i, "value": i} for i in sorted(categories.ExpenseCategory)]



@app.callback(
    Output("filters-store", "data"),
    Input("ExpenseCategory", "value"),
    Input("ExpenseDate", "start_date"),
    Input("ExpenseDate", "end_date"),
    State("filters-store", "data"),
)
def update_filters_store(
    ExpenseCategory,start_date,end_date,data
):
    data["ExpenseCategory"] = ExpenseCategory
    data["ExpenseDate"] = [start_date,end_date]
    return data


@app.callback(
    Output("ExpenseCategory", "value"),
    Output("ExpenseDate", "start_date"),
    Output("ExpenseDate", "end_date"),
    Input("clear-filters-btn", "n_clicks"),
)
def clear_all_filters(n):
    if n == 0:
        return [["Food"], date.today() - timedelta(days=30), date.today()]
    categories = data_connector.get_available_categories().ExpenseCategory
    return [categories, None, None]


@app.callback(Output("filter-tooltip", "children"), Input("filter-collapse", "is_open"))
def change_tooltip_message(is_open):
    if is_open:
        return "Click to hide filters"
    return "Click to show filters"


# Metric card callbacks
@app.callback(
    Output({"type": "metric-value", "index": "total-balance"}, "children"),
    Input("filters-store", "data"),
)
def display_total_balance(filters):
    return f"{data_connector.get_total_balance(filters):,}"


@app.callback(
    Output({"type": "metric-value", "index": "saving"}, "children"),
    Input("filters-store", "data"),
)
def display_total_savings(filters):
    saving_goal = data_connector.get_savings_goal(filters)
    if pd.isna(saving_goal) or pd.isnull(saving_goal):
        return "_"
    return f"{saving_goal:,}"



# Figure callbacks
@app.callback(
    Output({"type": "graph", "index": "spend-summary"}, "figure"),
    Input("filters-store", "data"),
)
def summary_figure(filters):
    data = data_connector.get_overview_data(filters)

    figure = px.bar(
        data,
        x="ExpenseCategory",
        y="TotalExpenses",
        labels={
            "ExpenseCategory": "Expense Category",
            "TotalExpenses": "Total Expenses",
        },
    )

    return figure



@app.callback(
    Output({"type": "graph", "index": "growth"}, "figure"),
    Input("filters-store", "data"),
)
def recent_content_figure(filters):
    data = data_connector.get_change_data(filters)
    category_order = [
        i for i in data_connector.category_order if i in set(data.ExpenseCategory)
    ]

    categories = pd.Series(category_order)
    data.set_index('ExpenseCategory', inplace=True)

    figure = go.Figure(
        data=[
            go.Bar(
                x=categories,
                y=categories.apply(lambda x: data.loc[x, 'net_change']),
                marker={'color' : 'blue', 'opacity' : 0.5},
                name='Net Change',
                hovertemplate='<b>Net Change: %{y}</b><extra></extra>'
            ),
        ],
        layout=go.Layout(
            showlegend=False,
            xaxis={
                'title' : 'Category',
                'ticktext' : categories,
                'tickangle' : 45
            },
            yaxis={
                'title' : 'Total'
            },
            template='plotly_white',
            hovermode='x unified',
        )
    )

    return figure


if __name__ == "__main__":
    app.run(debug=True)
