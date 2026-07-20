"""Data Visualization for Diamond Dataset"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# Load the dataset
df = pd.read_csv("data/diamonds.csv")

print(df.shape)
print(df.dtypes)
print(df.head())
print(df.describe())
print(df.isnull().sum())

#Cleaning the dataset
df = df.drop(columns=['Unnamed: 0'])

invalid_dims = df[(df["x"] == 0) | (df["y"] == 0) | (df["z"] == 0)]
print(f"Rows with zero dimensions: {len(invalid_dims)}")

outliers = df[(df["y"] > 20) | (df["z"] > 20)]
print(f"Rows with extreme y/z outliers: {len(outliers)}")
print(outliers)

df = df[(df["x"] > 0) & (df["y"] > 0) & (df["z"] > 0)]
df = df[(df["y"] < 20) & (df["z"] < 20)]

print(f"Final cleaned shape: {df.shape}")


cut_order = ["Fair", "Good", "Very Good", "Premium", "Ideal"]
color_order = ["J", "I", "H", "G", "F", "E", "D"]
clarity_order = ["I1", "SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF"]

df["cut"] = pd.Categorical(df["cut"], categories=cut_order, ordered=True)
df["color"] = pd.Categorical(df["color"], categories=color_order, ordered=True)
df["clarity"] = pd.Categorical(df["clarity"], categories=clarity_order, ordered=True)

#1st plot: Scatter plot of price vs carat colored by cut quality
plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=df,
    x="carat",
    y="price",
    hue="cut",
    palette="viridis",
    alpha=0.6,
    s=20,
)
plt.title("Diamond Price vs Carat According to Quality of Cut")
plt.xlabel("Carat")
plt.ylabel("Price (USD)")
plt.legend(title="Cut", bbox_to_anchor=(1.02, 1), loc='upper left')
plt.xlim(0, None)
plt.ylim(0, None)
plt.tight_layout()
plt.savefig("carat_vs_price_by_cut_quality.png", dpi=150)
plt.close()

#2nd plot: Boxplot of price by clarity
plt.figure(figsize=(10, 6))
sns.boxplot(
    data=df,
    x="clarity",
    y="price",
    hue="clarity",
    palette="viridis",
    legend=False,
    flierprops={"markerfacecolor": "gray", "markeredgecolor": "gray", "alpha": 0.4},
)

plt.title("Diamond Price Distribution by Clarity Grade")
plt.xlabel("Clarity (worst → best: I1 to IF)")
plt.ylabel("Price (USD)")
plt.ylim(0, df["price"].max() * 1.05)
plt.tight_layout()
plt.savefig("price_by_clarity.png", dpi=150)
plt.close()

#3rd plot: Interactive plot using plotly
fig = px.scatter(
    df.sort_values("color"),
    x="carat",
    y="price",
    color="cut",
    animation_frame="color",
    hover_data=["clarity", "depth", "table"],
    color_discrete_sequence=px.colors.sequential.Viridis[::2],
    title="Diamond Price vs. Carat by Cut, Animated Across Color Grade (J=worst → D=best)",
    labels={"carat": "Carat", "price": "Price (USD)", "cut": "Cut"},
    range_x=[0, df["carat"].max() * 1.05],
    range_y=[0, df["price"].max() * 1.05],
)
fig.update_traces(marker={"size": 5, "opacity": 0.6})
fig.write_html("carat_price_interactive.html")
