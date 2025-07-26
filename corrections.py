import json

try:
    with open("corrections.json", "r", encoding="utf-8") as f:
        corrections = json.load(f)
except Exception as e:
    print(f"❌ No se pudo cargar corrections.json: {e}")
    corrections = {}

def apply_corrections(text):
    for wrong, right in corrections.items():
        text = text.replace(wrong, right)
    return text
