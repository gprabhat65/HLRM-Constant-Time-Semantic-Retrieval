import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

from backend.app.core.pipeline import pipeline
from backend.app.core.retrieval import retriever

def test_pipeline():
    print("Testing Ingestion...")
    
    # Create dummy file
    dummy_path = os.path.join(os.getcwd(), 'backend', 'test_doc.txt')
    with open(dummy_path, 'w') as f:
        f.write("Attendance Policy:\nStudents must maintain 75% attendance to appear for exams.\n\nHostel Curfew:\nStudents must be in by 10 PM.")
    
    # Compile
    # We pass the absolute path
    count = pipeline.compile_knowledge([dummy_path])
    print(f"Compiled {count} items.")
    
    # Reload Retrieval
    retriever.load_knowledge()
    
    # Query 1
    q1 = "What is the attendance policy?"
    print(f"\nQuery: {q1}")
    res1 = retriever.query(q1)
    print(f"Result: {res1}")
    
    # Query 2 (Synonym)
    q2 = "minimum attendance requirement" 
    # 'policy' -> 'requirement'. 'Attendance Policy' -> 'attendance requirement'.
    # User query 'minimum attendance requirement'. 'minimum' might remain. 
    # 'attendance requirement' vs 'minimum attendance requirement'. Match fail unless 'minimum' is stopword.
    
    print(f"\nQuery: {q2}")
    res2 = retriever.query(q2)
    print(f"Result: {res2}")
    
    # Query 3 (Exact correct synonym)
    q3 = "attendance requirement"
    print(f"\nQuery: {q3}")
    res3 = retriever.query(q3)
    print(f"Result: {res3}")

    # Clean up
    if os.path.exists(dummy_path):
        os.remove(dummy_path)

if __name__ == "__main__":
    test_pipeline()
