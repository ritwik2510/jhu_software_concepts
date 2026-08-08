

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import json

MODEL_PATH = "./saved_model"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

with open(f"{MODEL_PATH}/metadata.json") as f:
    metadata = json.load(f)

MAX_LENGTH = metadata["max_length"]
LABEL_MAP = metadata["label_map"]

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

def format_value(val):
    if val is None or val == "":
        return "Unknown"
    return val

def build_input_text(program, term, degree, citizenship, gpa, gre, gre_v, gre_aw, comments):
    return (
        f"Program: {format_value(program)}\n"
        f"Term: {format_value(term)}\n"
        f"Degree: {format_value(degree)}\n"
        f"Citizenship: {format_value(citizenship)}\n"
        f"GPA: {format_value(gpa)}\n"
        f"GRE Quant: {format_value(gre)}\n"
        f"GRE Verbal: {format_value(gre_v)}\n"
        f"GRE AW: {format_value(gre_aw)}\n"
        f"Comments: {format_value(comments)}"
    )

def predict(program, term, degree, citizenship, gpa, gre, gre_v, gre_aw, comments):
    text = build_input_text(program, term, degree, citizenship, gpa, gre, gre_v, gre_aw, comments)
    inputs = tokenizer(text, truncation=True, padding=True, max_length=MAX_LENGTH, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)[0]

    pred_class = int(torch.argmax(probs).item())
    confidence = float(probs[pred_class].item())

    return {
        "prediction": LABEL_MAP[str(pred_class)],
        "confidence": round(confidence, 3)
    }

if __name__ == "__main__":
    result1 = predict("Computer Science", "Fall 2026", "PhD", "International", 3.9, 168, 160, 4.5, "Strong research background")
    result2 = predict("History", "Fall 2026", "Masters", "American", 3.1, None, None, None, "")

    print("=== STEP 6: RELOAD + INFERENCE CHECK ===")
    print("Example 1:", result1)
    print("Example 2:", result2)
