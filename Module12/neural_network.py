import json
import logging

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.FileHandler("training.log", mode="w"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

DATA_PATH = "llm_extend_applicant_data_run.jsonl"

RANDOM_SEED = 42
HIDDEN_UNITS = 6
LEARNING_RATE = 0.05
MAX_EPOCHS = 10000
PATIENCE = 100


# Section 1: Load and Prepare the Applicant Dataset
def load_raw_records(path):
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


# Section 2: Split and Preprocess the Data
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


# Section 3: Build a Two-Layer Neural Network in NumPy
def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def sigmoid_derivative(a):
    return a * (1 - a)


# W1 has shape (6, 6): maps the 6 input features to 6 hidden units.
# b1 has shape (1, 6): one bias per hidden unit.
# W2 has shape (6, 1): maps the 6 hidden units to 1 output unit.
# b2 has shape (1, 1): one bias for the output unit.
# The hidden layer computes a weighted sum of the 6 input features (X @ W1 + b1),
# then applies sigmoid, letting the network model nonlinear interactions between
# features (e.g. GPA and GRE together may matter differently than either alone).
# The output layer takes the hidden layer's activations and computes one more
# weighted sum (a1 @ W2 + b2), then applies sigmoid again, producing a single
# value between 0 and 1.
# Because sigmoid's range is exactly (0, 1), and training pushes this value
# toward 1 for accepted applicants and 0 for rejected ones, the output can be
# read as a probability-like score of acceptance.
class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size, seed=RANDOM_SEED):
        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(0, 0.1, size=(input_size, hidden_size))
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = rng.normal(0, 0.1, size=(hidden_size, output_size))
        self.b2 = np.zeros((1, output_size))
        self.z1 = None
        self.a1 = None
        self.z2 = None
        self.a2 = None

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


def compute_mse(predictions, targets):
    return np.mean((predictions - targets) ** 2)


def compute_accuracy(predictions, targets, threshold=0.5):
    predicted_labels = (predictions >= threshold).astype(int)
    return np.mean(predicted_labels == targets)


# Section 4: Train the Model Until Test MSE Stops Improving
model = NeuralNetwork(input_size=6, hidden_size=HIDDEN_UNITS, output_size=1)

history = {
    "epoch": [],
    "train_mse": [],
    "test_mse": [],
    "test_accuracy": [],
}

best_test_mse = np.inf
best_epoch = 0
best_weights = None
epochs_without_improvement = 0

for epoch in range(1, MAX_EPOCHS + 1):
    train_output = model.forward(X_train)
    train_mse = compute_mse(train_output, y_train)
    model.backward(X_train, y_train, train_output, LEARNING_RATE)

    test_output = model.forward(X_test)
    test_mse = compute_mse(test_output, y_test)
    test_accuracy = compute_accuracy(test_output, y_test)

    history["epoch"].append(epoch)
    history["train_mse"].append(train_mse)
    history["test_mse"].append(test_mse)
    history["test_accuracy"].append(test_accuracy)

    if test_mse < best_test_mse:
        best_test_mse = test_mse
        best_epoch = epoch
        best_weights = {
            "W1": model.W1.copy(),
            "b1": model.b1.copy(),
            "W2": model.W2.copy(),
            "b2": model.b2.copy(),
        }
        epochs_without_improvement = 0
    else:
        epochs_without_improvement += 1

    if epoch % 100 == 0:
        logger.info(
            "Epoch %d: train_mse=%.5f, test_mse=%.5f, test_accuracy=%.4f",
            epoch, train_mse, test_mse, test_accuracy
        )

    if epochs_without_improvement >= PATIENCE:
        logger.info("Early stopping at epoch %d", epoch)
        break

model.W1 = best_weights["W1"]
model.b1 = best_weights["b1"]
model.W2 = best_weights["W2"]
model.b2 = best_weights["b2"]


# Section 5: Evaluate the Final Model
final_train_output = model.forward(X_train)
final_train_accuracy = compute_accuracy(final_train_output, y_train)

final_test_output = model.forward(X_test)
final_test_accuracy = compute_accuracy(final_test_output, y_test)

logger.info("Best epoch: %d", best_epoch)
logger.info("Best test MSE: %.5f", best_test_mse)
logger.info("Final training accuracy: %.4f", final_train_accuracy)
logger.info("Final test accuracy: %.4f", final_test_accuracy)
logger.info("Rows used after filtering: %d", filtered_row_count)
logger.info("Training set size: %d", X_train.shape[0])
logger.info("Test set size: %d", X_test.shape[0])


# Section 6: Plot Train and Test MSE Over Time
plt.figure(figsize=(8, 5))
plt.plot(history["epoch"], history["train_mse"], label="Training MSE")
plt.plot(history["epoch"], history["test_mse"], label="Test MSE")
plt.title("Training and Test MSE Over Epochs")
plt.xlabel("Epoch")
plt.ylabel("Mean Squared Error")
plt.legend()
plt.savefig("mse_curve.png")
plt.close()


# Section 7: Test the Model on Artificial Applicants
artificial_applicants = pd.DataFrame([
    {
        "name": "Strong PhD applicant (international)",
        "gpa": 3.95,
        "gre": 332.0,
        "gre_v": 168.0,
        "gre_aw": 5.0,
        "ms_vs_phd": 1,
        "international_vs_local": 1,
    },
    {
        "name": "Average Masters applicant (local)",
        "gpa": 3.30,
        "gre": 300.0,
        "gre_v": 152.0,
        "gre_aw": 3.5,
        "ms_vs_phd": 0,
        "international_vs_local": 0,
    },
])

artificial_features = artificial_applicants[feature_columns].to_numpy(dtype=float)
artificial_features = np.where(
    np.isnan(artificial_features), train_medians, artificial_features
)
artificial_features_scaled = (artificial_features - train_means) / train_stds

artificial_probabilities = model.predict_proba(artificial_features_scaled)
artificial_labels = model.predict(artificial_features_scaled)

artificial_applicants["predicted_probability"] = artificial_probabilities
artificial_applicants["predicted_label"] = artificial_labels
artificial_applicants["predicted_status"] = np.where(
    artificial_labels == 1, "Accepted", "Rejected"
)

print(artificial_applicants)