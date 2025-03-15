import json
import dash_bootstrap_components as dbc
from dash import html, dcc

from .components.MetricCard import MetricCard
from .components.FigureCard import FigureCard

with open("F:\\Accountly\\assets\\figure_descriptions.json", "r") as f:
    figure_descriptions = json.load(f)

dashboard = dbc.Row(
    dbc.Col(
        [
            dbc.Row(
                [
                    dbc.Col(MetricCard("Current Balance in EGP", id="total-balance"), width=4),
                    dbc.Col(MetricCard("Savings Goal", id="saving"), width=4),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        FigureCard(
                            "Spending Overview",
                            id="spend-summary",
                            description=figure_descriptions.get("summary"),
                        ),
                        sm=12,
                        md=7,
                    ),
                ],
                className="dashboard-row",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        FigureCard(
                            "Expenses Change",
                            id="growth",
                            description=figure_descriptions.get("growth"),
                        ),
                        sm=12,
                        md=12,
                    ),
                ],
                className="dashboard-row",
            ),
        ],
    ),
    id="dashboard",
)
