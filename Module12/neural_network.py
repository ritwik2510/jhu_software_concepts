""" Code for Neural Network"""

import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

DATA_PATH = "llm_extend_applicant_data_run.jsonl"

def load_raw_records(path):
    """loads raw records"""
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


raw_records = load_raw_records(DATA_PATH)
raw_df = pd.DataFrame(raw_records)
original_row_count = len(raw_df)

raw_df["applicant_status"] = raw_df["status"].str.split(" on ").str[0]

raw_df = raw_df.rename(columns={
    "GPA": "gpa",
    "GRE": "gre",
    "GRE V": "gre_v",
    "GRE AW": "gre_aw",
    "Degree": "masters_or_phd",
    "US/International": "citizenship",
})

filtered_df = raw_df[
    raw_df["applicant_status"].isin(["Accepted", "Rejected"])
    & raw_df["masters_or_phd"].isin(["Masters", "PhD"])
].copy()

for col in ["gpa", "gre", "gre_v", "gre_aw"]:
    filtered_df[col] = pd.to_numeric(filtered_df[col], errors="coerce")

filtered_df["ms_vs_phd"] = (filtered_df["masters_or_phd"] == "PhD").astype(int)
filtered_df["international_vs_local"] = (filtered_df["citizenship"] == "International").astype(int)
filtered_df["target"] = (filtered_df["applicant_status"] == "Accepted").astype(int)

feature_columns = ["gpa", "gre", "gre_v", "gre_aw", "ms_vs_phd", "international_vs_local"]

filtered_row_count = len(filtered_df)
accepted_count = (filtered_df["applicant_status"] == "Accepted").sum()
rejected_count = (filtered_df["applicant_status"] == "Rejected").sum()

print(f"Original row count: {original_row_count}")
print(f"Filtered row count: {filtered_row_count}")
print(f"Accepted count: {accepted_count}")
print(f"Rejected count: {rejected_count}")
print(f"Final input features: {feature_columns}")
print(filtered_df[feature_columns + ['target']].head())

X = filtered_df[feature_columns].to_numpy(dtype=float)
y = filtered_df["target"].to_numpy(dtype=float).reshape(-1, 1)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, shuffle=True
)

train_medians = np.nanmedian(X_train, axis=0)
X_train = np.where(np.isnan(X_train), train_medians, X_train)
X_test = np.where(np.isnan(X_test), train_medians, X_test)

train_means = X_train.mean(axis=0)
train_stds = X_train.std(axis=0)
train_stds = np.where(train_stds == 0, 1, train_stds)

X_train = (X_train - train_means) / train_stds
X_test = (X_test - train_means) / train_stds

print(f"Training set size: {X_train.shape[0]}")
print(f"Test set size: {X_test.shape[0]}")
print(f"Training-set medians: {dict(zip(feature_columns, train_medians))}")
print(f"Training-set means: {dict(zip(feature_columns, train_means))}")
print(f"Training-set standard deviations: {dict(zip(feature_columns, train_stds))}")

RANDOM_SEED = 42
HIDDEN_UNITS = 6
LEARNING_RATE = 0.05
MAX_EPOCHS = 10000
PATIENCE = 100


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def sigmoid_derivative(a):
    return a * (1 - a)


class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size, seed=RANDOM_SEED):
        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(0, 0.1, size=(input_size, hidden_size))
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = rng.normal(0, 0.1, size=(hidden_size, output_size))
        self.b2 = np.zeros((1, output_size))

    def forward(self, X):
        self.z1 = X @ self.W1 + self.b1
        self.a1 = sigmoid(self.z1)
        self.z2 = self.a1 @ self.W2 + self.b2
        self.a2 = sigmoid(self.z2)
        return self.a2

    def backward(self, X, y, output, learning_rate):
        n = X.shape[0]

        error_output = output - y
        delta_output = error_output * sigmoid_derivative(output)

        error_hidden = delta_output @ self.W2.T
        delta_hidden = error_hidden * sigmoid_derivative(self.a1)

        dW2 = self.a1.T @ delta_output / n
        db2 = np.sum(delta_output, axis=0, keepdims=True) / n
        dW1 = X.T @ delta_hidden / n
        db1 = np.sum(delta_hidden, axis=0, keepdims=True) / n

        self.W2 -= learning_rate * dW2
        self.b2 -= learning_rate * db2
        self.W1 -= learning_rate * dW1
        self.b1 -= learning_rate * db1

    def predict_proba(self, X):
        return self.forward(X)

    def predict(self, X, threshold=0.5):
        return (self.predict_proba(X) >= threshold).astype(int)