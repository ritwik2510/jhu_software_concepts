"""Data visualization for the Diamond dataset."""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px


DATA_PATH = "data/diamonds.csv"
ASSETS_DIR = "assets"


def load_and_clean_data():
    """Load and clean the diamond dataset."""
    df = pd.read_csv(DATA_PATH)

    print(f"Original shape: {df.shape}")
    print(df.dtypes)
    print(df.head())
    print(df.describe())
    print("\nMissing values:")
    print(df.isnull().sum())

    # Remove leftover CSV index column.
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # Identify invalid dimensions.
    invalid_dims = df[
        (df["x"] == 0)
        | (df["y"] == 0)
        | (df["z"] == 0)
    ]

    print(f"Rows with zero dimensions: {len(invalid_dims)}")

    # Identify extreme y/z outliers.
    outliers = df[
        (df["y"] > 20)
        | (df["z"] > 20)
    ]

    print(f"Rows with extreme y/z outliers: {len(outliers)}")
    print(outliers)

    # Remove invalid dimensions and extreme outliers.
    df = df[
        (df["x"] > 0)
        & (df["y"] > 0)
        & (df["z"] > 0)
    ]

    df = df[
        (df["y"] < 20)
        & (df["z"] < 20)
    ]

    print(f"Final cleaned shape: {df.shape}")

    # Set logical ordering for categorical variables.
    cut_order = [
        "Fair",
        "Good",
        "Very Good",
        "Premium",
        "Ideal",
    ]

    color_order = [
        "J",
        "I",
        "H",
        "G",
        "F",
        "E",
        "D",
    ]

    clarity_order = [
        "I1",
        "SI2",
        "SI1",
        "VS2",
        "VS1",
        "VVS2",
        "VVS1",
        "IF",
    ]

    df["cut"] = pd.Categorical(
        df["cut"],
        categories=cut_order,
        ordered=True,
    )

    df["color"] = pd.Categorical(
        df["color"],
        categories=color_order,
        ordered=True,
    )

    df["clarity"] = pd.Categorical(
        df["clarity"],
        categories=clarity_order,
        ordered=True,
    )

    return df


def create_carat_cut_plot(df):
    """Create a carat versus price scatter plot grouped by cut."""
    plt.figure(figsize=(10, 6))

    sns.scatterplot(
        data=df,
        x="carat",
        y="price",
        hue="cut",
        palette="viridis",
        alpha=0.35,
        s=12,
    )

    plt.title("Diamond Price vs. Carat by Cut Quality")
    plt.xlabel("Carat Weight")
    plt.ylabel("Price (USD)")
    plt.legend(
        title="Cut",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
    )

    plt.xlim(0, None)
    plt.ylim(0, None)
    plt.tight_layout()

    plt.savefig(
        f"{ASSETS_DIR}/carat_vs_price_by_cut_quality.png",
        dpi=150,
    )

    plt.close()


def create_clarity_plot(df):
    """Create a boxplot showing price distributions by clarity."""
    plt.figure(figsize=(10, 6))

    sns.boxplot(
        data=df,
        x="clarity",
        y="price",
        hue="clarity",
        palette="viridis",
        legend=False,
        flierprops={
            "markerfacecolor": "gray",
            "markeredgecolor": "gray",
            "alpha": 0.4,
        },
    )

    plt.title("Diamond Price Distribution by Clarity Grade")
    plt.xlabel("Clarity (Worst → Best: I1 to IF)")
    plt.ylabel("Price (USD)")
    plt.ylim(0, df["price"].max() * 1.05)

    plt.tight_layout()

    plt.savefig(
        f"{ASSETS_DIR}/price_by_clarity.png",
        dpi=150,
    )

    plt.close()


def create_interactive_plot(df):
    """Create an interactive carat versus price visualization."""
    sorted_df = df.sort_values("color")

    fig = px.scatter(
        sorted_df,
        x="carat",
        y="price",
        color="cut",
        animation_frame="color",
        hover_data=[
            "clarity",
            "depth",
            "table",
        ],
        color_discrete_sequence=px.colors.sequential.Viridis[::2],
        title=(
            "Diamond Price vs. Carat by Cut, "
            "Animated Across Color Grade "
            "(J = worst → D = best)"
        ),
        labels={
            "carat": "Carat Weight",
            "price": "Price (USD)",
            "cut": "Cut Quality",
        },
        range_x=[
            0,
            df["carat"].max() * 1.05,
        ],
        range_y=[
            0,
            df["price"].max() * 1.05,
        ],
    )

    fig.update_traces(
        marker={
            "size": 5,
            "opacity": 0.6,
        }
    )

    fig.write_html(
        f"{ASSETS_DIR}/carat_price_interactive.html"
    )


def main():
    """Run the complete visualization pipeline."""
    df = load_and_clean_data()

    create_carat_cut_plot(df)
    create_clarity_plot(df)
    create_interactive_plot(df)

    print("\nVisualization files created in assets/.")


if __name__ == "__main__":
    main()
