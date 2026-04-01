import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

from backend.app.core.pipeline import pipeline
from backend.app.core.config import KNOWLEDGE_STORE_PATH

print(f"Target Store Path: {KNOWLEDGE_STORE_PATH}")

# Data files
data_dir = os.path.dirname(KNOWLEDGE_STORE_PATH)
files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.txt')]

print(f"Found input files: {files}")

count = pipeline.compile_knowledge(files)
print(f"Compiled {count} entries.")

if os.path.exists(KNOWLEDGE_STORE_PATH):
    print("SUCCESS: File generated.")
else:
    print("FAILURE: File not generated.")
