import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = os.path.join(BASE_DIR, "data")
KNOWLEDGE_STORE_PATH = os.path.join(DATA_DIR, "knowledge_store.json")

os.makedirs(DATA_DIR, exist_ok=True)
