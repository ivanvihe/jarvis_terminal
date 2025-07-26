import json

class Memory:
    def __init__(self, filename="memory.json"):
        self.filename = filename
        self.data = self.load()

    def load(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    def append(self, item):
        self.data.append(item)

    def save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)