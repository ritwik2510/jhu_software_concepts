"""Dash dashboard for the Diamond Price Analysis project."""

from dash import Dash, html


app = Dash(__name__)

app.layout = html.Div(
    style={
        "fontFamily": "Arial, sans-serif",
        "margin": "40px",
        "maxWidth": "1200px",
        "marginLeft": "auto",
        "marginRight": "auto",
    },
    children=[
        html.H1(
            "Can the Price of a Diamond Be Determined "
            "Based Upon Its Features?"
        ),

        html.P(
            "This analysis examines whether diamond price can be "
            "estimated from carat weight, cut, color, and clarity."
        ),

        html.H2(
            "Sub-question 1: How strongly is carat related to price?"
        ),

        html.P(
            "Larger diamonds generally cost more, and the relationship "
            "is non-linear. The effect of carat weight is visible across "
            "all levels of cut quality."
        ),

        html.Img(
            src="/assets/carat_vs_price_by_cut_quality.png",
            style={
                "maxWidth": "100%",
                "width": "100%",
            },
        ),

        html.H2(
            "Sub-question 2: How does clarity relate to diamond price?"
        ),

        html.P(
            "Price distributions vary across clarity grades, but clarity "
            "alone does not determine price. Carat weight is an important "
            "confounding factor because larger diamonds can have lower "
            "clarity while still having high prices."
        ),

        html.Img(
            src="/assets/price_by_clarity.png",
            style={
                "maxWidth": "100%",
                "width": "100%",
            },
        ),

        html.H2(
            "Sub-question 3: Does the carat-price relationship "
            "remain across color grades?"
        ),

        html.P(
            "The interactive visualization shows that the non-linear "
            "relationship between carat and price remains across the "
            "different color grades."
        ),

        html.Iframe(
            src="/assets/carat_price_interactive.html",
            style={
                "width": "100%",
                "height": "650px",
                "border": "none",
            },
        ),

        html.H2("Conclusion"),

        html.P(
            "Diamond price can reasonably be estimated from its features, "
            "but no single feature completely determines price. Carat "
            "weight is the strongest visible driver, while cut, color, "
            "and clarity provide additional information."
        ),
    ],
)


if __name__ == "__main__":
    app.run(debug=True)
