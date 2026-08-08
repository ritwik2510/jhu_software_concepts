"""code for training the model"""

import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer
import torch
from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.metrics import confusion_matrix, classification_report

# Load and Prepare the Applicant Dataset

df = pd.read_json("data/llm_extend_applicant_data_run.jsonl", lines=True)

print("Original row count:", len(df))
print("Columns:", list(df.columns))
print(df.head(3))

print("\nUnique status values (sample):")
print(df["status"].dropna().unique()[:20])

print("\nMissing value counts:")
print(df[["program", "comments", "status", "GPA", "GRE", "GRE V", "GRE AW", "Degree", "US/International"]].isna().sum())

df["status_clean"] = df["status"].str.extract(r"^(Accepted|Rejected)")

df = df[df["status_clean"].notna()].copy()

df["label"] = (df["status_clean"] == "Accepted").astype(int)

df = df.drop_duplicates(subset="url", keep="first")

print("\nRows after status filter + dedup:", len(df))
print("Accepted count:", (df["label"] == 1).sum())
print("Rejected count:", (df["label"] == 0).sum())

numeric_cols = ["GPA", "GRE", "GRE V", "GRE AW"]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

text_cols = ["program", "comments", "term", "Degree", "US/International"]

for col in text_cols:
    df[col] = df[col].fillna("Unknown").astype(str).str.strip()
    df[col] = df[col].replace("", "Unknown")

print("\nFinal dtypes:")
print(df[numeric_cols + text_cols].dtypes)

print("\nFinal missing value counts (numeric):")
print(df[numeric_cols].isna().sum())

print("\nPreview of cleaned data:")
print(df[["program", "comments", "status_clean", "label", "Degree", "US/International", "GPA", "GRE", "GRE V", "GRE AW"]].head(5))

fields_used = ["program", "comments", "term", "Degree", "US/International", "GPA", "GRE", "GRE V", "GRE AW"]

print("\n=== STEP 1 SUMMARY ===")
print("Original row count:", 36000)
print("Rows after filtering:", len(df))
print("Accepted rows:", (df["label"] == 1).sum())
print("Rejected rows:", (df["label"] == 0).sum())
print("Fields used for modeling:", fields_used)
print("\nCleaned dataframe preview:")
print(df[fields_used + ["label"]].head(5))

#Unified Text Template
def format_value(val):
    if pd.isna(val):
        return "Unknown"
    return val

def build_model_input(row):
    text = (
        f"Program: {row['program']}\n"
        f"Term: {row['term']}\n"
        f"Degree: {row['Degree']}\n"
        f"Citizenship: {row['US/International']}\n"
        f"GPA: {format_value(row['GPA'])}\n"
        f"GRE Quant: {format_value(row['GRE'])}\n"
        f"GRE Verbal: {format_value(row['GRE V'])}\n"
        f"GRE AW: {format_value(row['GRE AW'])}\n"
        f"Comments: {row['comments']}"
    )
    return text

df["model_input"] = df.apply(build_model_input, axis=1)

print("\n=== STEP 2: MODEL INPUT TEMPLATE ===")
print("\nSample model inputs:\n")
for i in range(3):
    print(f"--- Example {i+1} (label={df.iloc[i]['label']}) ---")
    print(df.iloc[i]["model_input"])
    print()

#Train/Test Split

X = df["model_input"]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    shuffle=True,
    stratify=y
)

print("\n=== STEP 3: TRAIN/TEST SPLIT ===")
print("Training set size:", len(X_train))
print("Test set size:", len(X_test))
print("\nTraining class balance:")
print(y_train.value_counts(normalize=True))
print("\nTest class balance:")
print(y_test.value_counts(normalize=True))

# Finetuning DistilBERT

MODEL_NAME = "distilbert-base-uncased"
MAX_LENGTH = 256

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

train_encodings = tokenizer(
    list(X_train),
    truncation=True,
    padding=True,
    max_length=MAX_LENGTH
)

test_encodings = tokenizer(
    list(X_test),
    truncation=True,
    padding=True,
    max_length=MAX_LENGTH
)

print("\n=== STEP 4a: TOKENIZATION ===")
print("Model:", MODEL_NAME)
print("Max length:", MAX_LENGTH)
print("Sample tokenized input IDs (first 20 tokens):")
print(train_encodings["input_ids"][0][:20])
print("Sample decoded back:")
print(tokenizer.decode(train_encodings["input_ids"][0][:50]))



class GradCafeDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = list(labels)

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = GradCafeDataset(train_encodings, y_train)
test_dataset = GradCafeDataset(test_encodings, y_test)

model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average="binary")
    acc = accuracy_score(labels, preds)
    return {"accuracy": acc, "precision": precision, "recall": recall, "f1": f1}

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    learning_rate=2e-5,
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_steps=50,
    load_best_model_at_end=True,
    metric_for_best_model="f1",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    compute_metrics=compute_metrics,
)

print("\n=== STEP 4b: TRAINING CONFIG ===")
print("Model:", MODEL_NAME)
print("Tokenizer:", MODEL_NAME)
print("Max sequence length:", MAX_LENGTH)
print("Batch size:", 16)
print("Epochs:", 3)
print("Learning rate:", 2e-5)
print("Optimizer: AdamW (default in Trainer)")
print("Device:", device)

print("\n=== STARTING TRAINING ===")
train_result = trainer.train()

print("\n=== TRAINING COMPLETE ===")
print(train_result)

#Final Evaluation

print("\n=== STEP 5: FINAL EVALUATION ===")

predictions = trainer.predict(test_dataset)
preds = predictions.predictions.argmax(-1)
probs = torch.softmax(torch.tensor(predictions.predictions), dim=1)[:, 1].numpy()
true_labels = predictions.label_ids

acc = accuracy_score(true_labels, preds)
precision, recall, f1, _ = precision_recall_fscore_support(true_labels, preds, average="binary")
cm = confusion_matrix(true_labels, preds)

print(f"Accuracy: {acc:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1: {f1:.4f}")
print("\nConfusion Matrix:")
print(cm)
print("\nClass distribution (test set):")
print(pd.Series(true_labels).value_counts())

print("\nFull classification report:")
print(classification_report(true_labels, preds, target_names=["Rejected", "Accepted"]))

print("\n--- Sample predictions with probabilities ---")
X_test_reset = X_test.reset_index(drop=True)
for i in range(5):
    print(f"True: {true_labels[i]} | Pred: {preds[i]} | Prob(Accepted): {probs[i]:.3f}")

print("\n--- Correctly classified examples ---")
correct_idx = [i for i in range(len(preds)) if preds[i] == true_labels[i]][:2]
for i in correct_idx:
    print(f"[CORRECT] True: {true_labels[i]}, Pred: {preds[i]}, Prob: {probs[i]:.3f}")
    print(X_test_reset.iloc[i][:150])
    print()

print("--- Incorrectly classified examples ---")
wrong_idx = [i for i in range(len(preds)) if preds[i] != true_labels[i]][:2]
for i in wrong_idx:
    print(f"[WRONG] True: {true_labels[i]}, Pred: {preds[i]}, Prob: {probs[i]:.3f}")
    print(X_test_reset.iloc[i][:150])
    print()


# Saving Model

print("\n=== STEP 6: SAVE MODEL ===")

SAVE_PATH = "./saved_model"

model.save_pretrained(SAVE_PATH)
tokenizer.save_pretrained(SAVE_PATH)

import json
metadata = {
    "label_map": {"0": "Rejected", "1": "Accepted"},
    "max_length": MAX_LENGTH,
    "model_name": MODEL_NAME
}
with open(f"{SAVE_PATH}/metadata.json", "w") as f:
    json.dump(metadata, f)

print("Model saved to", SAVE_PATH)