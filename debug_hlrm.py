import os
import json
import hashlib
import sys

# Emulate pipeline logic
def normalize(text):
    stop_words = {
        "what", "is", "the", "a", "an", "please", "tell", "me", "about", 
        "does", "do", "how", "why", "when", "where", "can", "could", "would", "should"
    }
    text = text.lower()
    import re
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()
    words = [w for w in words if w not in stop_words]
    return " ".join(words)

def get_hash(route, intent):
    return hashlib.sha256(f"{route}|{intent}".encode()).hexdigest()

print("--- DIAGNOSIS ---")
cwd = os.getcwd()
print(f"CWD: {cwd}")

# Check locations
paths_to_check = [
    os.path.join(cwd, "data", "knowledge_store.json"),
    os.path.join(cwd, "backend", "data", "knowledge_store.json"),
    os.path.join(cwd, "backend", "app", "data", "knowledge_store.json")
]

store_path = None
for p in paths_to_check:
    if os.path.exists(p):
        print(f"FOUND Store at: {p}")
        store_path = p 
    else:
        print(f"MISSING: {p}")

if store_path:
    with open(store_path, 'r') as f:
        data = json.load(f)
        print(f"Entries: {len(data)}")
        
        # Check specific key
        target_intent = "supplementary exams"
        routes = ["Root", "Root/Academics", "Root/Hostels"]
        
        found = False
        for r in routes:
            h = get_hash(r, target_intent)
            key = f"{r}|{h}"
            print(f"Checking Key: {key}")
            if key in data:
                print(f"  -> FOUND match! Value: {data.get(key)}")
                found = True
        
        if not found:
            print("  -> NO MATCH found for 'Supplementary Exams'")
            print("Top 5 Keys in Store:")
            for k in list(data.keys())[:5]:
                print(f"  {k} : {data[k].get('original_intent')} -> {data[k].get('answer')[:30]}...")

else:
    print("NO KNOWLEDGE STORE FOUND.")
