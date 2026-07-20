"""code for dashboard.py"""

from dash import Dash, html

app = Dash(__name__)

app.layout = html.Div(
    style={"fontFamily": "Arial, sans-serif", "margin": "40px"},
    children=[
        html.H1(
            "Can the Price of a Diamond Be Determined Based Upon Its Features?"
        ),
        html.P(
            "Carat is the strongest driver of price, but its effect is "
            "non-linear and large stones command a disproportionate premium. "
            "Clarity alone is misleading, since low-clarity stones tend to be "
            "large, high-carat pieces. Together, carat, cut, color, and "
            "clarity reliably explain a diamond's price.",
            style={"maxWidth": "800px"},
        ),
        html.H2("Carat vs. Price, by Cut Quality"),
        html.Img(
            src="/assets/carat_vs_price_by_cut_quality.png",
            style={"maxWidth": "900px", "width": "100%"},
        ),
        html.H2("Price Distribution by Clarity Grade"),
        html.Img(
            src="/assets/price_by_clarity.png",
            style={"maxWidth": "900px", "width": "100%"},
        ),
        html.H2("Interactive: Carat vs. Price, Animated by Color Grade"),
        html.Iframe(
            src="/assets/carat_price_interactive.html",
            style={"width": "100%", "height": "650px", "border": "none"},
        ),
    ],
)

if __name__ == "__main__":
    app.run(debug=True)
