import json
import re

INPUT_FILE = "applicant_data.json"
OUTPUT_FILE = "llm_extend_applicant_data.json"


def _clean_text(val):
    if val is None:
        return None
    val = val.strip()
    return val if val else None


def _extract1(text):
    if not text:
        return None
    match = re.search(r"\d+(\.\d+)?", str(text))
    return float(match.group()) if match else None


def _extract_int(text):
    if not text:
        return None
    match = re.search(r"\d+", str(text))
    return int(match.group()) if match else None


def _standardize_university(name):
    if not name:
        return None
    name = re.sub(r"\s*\([^)]*\)", "", name)
    name = name.strip()
    return name


def _standardize_program(name):
    if not name:
        return None
    name = re.sub(r"\s*\([^)]*\)", "", name)
    name = re.sub(r"\s*-\s*(DBA|MBA|MS|MA)\s*$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s+online\s*$", "", name, flags=re.IGNORECASE)
    name = name.strip()
    return name


def clean_record(record):
    cleaned = record.copy()

    for field in ["university", "program", "status", "comments", "term", "origin"]:
        cleaned[field] = _clean_text(cleaned.get(field))

    cleaned["gpa"] = _extract1(cleaned.get("GPA"))
    cleaned["gre"] = _extract_int(cleaned.get("GRE"))
    cleaned["gre_v"] = _extract_int(cleaned.get("GRE V"))
    cleaned["gre_aw"] = _extract1(cleaned.get("GRE AW"))

    status_lower = (cleaned.get("status") or "").lower()
    if "accepted" in status_lower:
        cleaned["status"] = "Accepted"
    elif "rejected" in status_lower:
        cleaned["status"] = "Rejected"
    elif "wait" in status_lower:
        cleaned["status"] = "Waitlisted"
    elif "interview" in status_lower:
        cleaned["status"] = "Interview"
    else:
        cleaned["status"] = "Unknown"

    cleaned["degree_type"] = cleaned.get("degree")
    cleaned["international"] = cleaned.get("origin")

    year_match = re.search(r"(20\d{2})", cleaned.get("term") or "")
    cleaned["year"] = int(year_match.group(1)) if year_match else None

    cleaned["llm_generated_university"] = _standardize_university(cleaned.get("university"))
    cleaned["llm_generated_program"] = _standardize_program(cleaned.get("program"))

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

    print(f"Cleaned {len(cleaned_data)} records and saved to {OUTPUT_FILE}")