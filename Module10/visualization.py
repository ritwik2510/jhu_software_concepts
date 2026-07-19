"""Data Visualization for Diamond Dataset"""

import pandas as pd

# Load the dataset
df = pd.read_csv("data/diamonds.csv")

# Initial exploration
print(df.shape)
print(df.dtypes)
print(df.head())
print(df.describe())
print(df.isnull().sum())

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
color_order = ["J", "I", "H", "G", "F", "E", "D"]  # J=worst, D=best
clarity_order = ["I1", "SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF"]

df["cut"] = pd.Categorical(df["cut"], categories=cut_order, ordered=True)
df["color"] = pd.Categorical(df["color"], categories=color_order, ordered=True)
df["clarity"] = pd.Categorical(df["clarity"], categories=clarity_order, ordered=True)