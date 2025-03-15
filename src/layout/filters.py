from datetime import date, timedelta
import dash_bootstrap_components as dbc
from dash import html, dcc

filters = dbc.Row(
    dbc.Col(
        dbc.Card(
            [
                dbc.CardHeader(
                    [
                        dbc.Tooltip(
                            "Click to show filters",
                            id="filter-tooltip",
                            placement="left",
                            target="filter-header-btn",
                        ),
                        dbc.Button(
                            [
                                html.P("Filters", className="m-0"),
                                html.Span(
                                    "keyboard_arrow_down",
                                    id="filter-header-icon",
                                    className="material-symbols-outlined",
                                ),
                            ],
                            id="filter-header-btn",
                            className="w-100 p-3 d-flex justify-content-between",
                            color="light",
                            n_clicks=0,
                        ),
                    ],
                    className="p-0 m-0",
                ),
                dbc.Collapse(
                    dbc.CardBody(
                        dbc.Stack(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label(
                                                    "Date",
                                                    html_for="date",
                                                ),
                                                dcc.DatePickerRange(
                                                    id='ExpenseDate',
                                                    min_date_allowed=date(1900, 1, 1),
                                                    max_date_allowed=date(2999, 12, 31),
                                                    initial_visible_month=date.today() - timedelta(days=30),
                                                    end_date=date.today(),
                                                    className="d-flex justify-content-evenly",
                                                    #inline=True,
                                                ),
                                            ],
                                            md=3,
                                            sm=12,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label(
                                                    "Category",
                                                    html_for="platform",
                                                ),
                                                dcc.Dropdown(
                                                    id="ExpenseCategory", multi=True, value=[]
                                                ),
                                            ],
                                            md=9,
                                            sm=12,
                                        ),
                                    ]
                                ),

                                dbc.Row(
                                    dbc.Col(
                                        dbc.Button(
                                            "Clear Filters",
                                            id="clear-filters-btn",
                                            color="link",
                                            n_clicks=0,
                                        ),
                                        className="d-flex justify-content-end",
                                    )
                                ),
                            ],
                            gap=3,
                        )
                    ),
                    id="filter-collapse",
                    is_open=False,
                ),
            ]
        )
    ),
    id="filters",
)
