import json
import re

INPUT_FILE = "applicant_data.json"
OUTPUT_FILE = "llm_extend_applicant_data.json"


def clean_text(val):
    if val is None:
        return None
    val = val.strip()
    return val if val else None


def extract1(text):
    if not text:
        return None
    match = re.search(r"\d+(\.\d+)?", str(text))
    return float(match.group()) if match else None

def extract_int(text):
    if not text:
        return None
    match = re.search(r"/d+", str(text))
    return int(match.group()) if match else None


def clean_record(record):

    cleaned = record.copy()

    for field in ["university", "program", "status", "comments"]:
        cleaned[field] = clean_text(cleaned.get(field))

    cleaned["gpa"] = extract1(cleaned.get("raw_text"))

    raw = cleaned.get("raw_text", "")

    gre_match = re.search(r"GRE[:\s]*(\d+)", raw, re.IGNORECASE)
    cleaned["gre"] = int(gre_match.group(1)) if gre_match else None

    gre_v_match = re.search(r"(verbal|v)[:\s]*(\d+)", raw, re.IGNORECASE)
    cleaned["gre_v"] = int(gre_v_match.group(2)) if gre_v_match else None

    gre_aw_match = re.search(r"(awa|writing)[:\s]*(\d+(\.\d+)?)", raw, re.IGNORECASE)
    cleaned["gre_aw"] = float(gre_aw_match.group(3)) if gre_aw_match else None

    text_lower = raw.lower()

    if "accept" in text_lower:
        cleaned["decision"] = "Accepted"
    elif "reject" in text_lower:
        cleaned["decision"] = "Rejected"
    else:
        cleaned["decision"] = "Unknown"

    
    if "phd" in text_lower or "ph.d" in text_lower:
        cleaned["degree_type"] = "PhD"
    elif "master" in text_lower or "ms" in text_lower:
        cleaned["degree_type"] = "Masters"
    else:
        cleaned["degree_type"] = None
    

    if "international" in text_lower:
        cleaned["international"] = "International"
    elif "american" in text_lower or "domestic" in text_lower or "us citizen" in text_lower:
        cleaned["international"] = "Domestic"
    else:
        cleaned["international"] = None
    

    year_match = re.search(r"(20\d{2})", raw)
    cleaned["year"] = int(year_match.group(1)) if year_match else None

    return cleaned


def clean_data(data):
    return [clean_record(record) for record in data]

def load_data():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    
def save_data(data):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    raw_data = load_data()
    cleaned_data = clean_data(raw_data)
    save_data(cleaned_data)

    print(f"Cleaned {len(cleaned_data)} and new file is {OUTPUT_FILE}")