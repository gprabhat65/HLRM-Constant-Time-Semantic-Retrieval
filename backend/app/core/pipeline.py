import hashlib
import json
import re
import os
from typing import List, Dict
import PyPDF2
import docx

from .config import KNOWLEDGE_STORE_PATH

# =========================================================
# Canonical Normalization (SINGLE SOURCE OF TRUTH)
# =========================================================

STOP_WORDS = {
    "what", "is", "the", "a", "an", "please", "tell", "me", "about",
    "does", "do", "how", "why", "when", "where", "can", "could",
    "would", "should", "explain", "define"
}

SYNONYMS = {
    "rule": "requirement",
    "rules": "requirement",
    "policy": "requirement",
    "criteria": "requirement",
    "marks": "grades",
    "mark": "grades",
    "score": "grades",
    "scoring": "grades",
    "attendance rule": "attendance requirement"
}


def normalize(text: str) -> str:
    """
    Canonical, deterministic normalization.
    MUST be identical in ingestion and runtime.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)

    words = [w for w in text.split() if w not in STOP_WORDS]

    normalized = []
    i = 0
    while i < len(words):
        # Bigram synonym check
        if i + 1 < len(words):
            bigram = f"{words[i]} {words[i+1]}"
            if bigram in SYNONYMS:
                normalized.append(SYNONYMS[bigram])
                i += 2
                continue

        normalized.append(SYNONYMS.get(words[i], words[i]))
        i += 1

    return " ".join(normalized).strip()


# =========================================================
# Semantic Hashing (PURE FUNCTION)
# =========================================================

def semantic_hash(route: str, normalized_intent: str) -> str:
    key = f"{route}|{normalized_intent}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


# =========================================================
# HLRM INGESTION PIPELINE
# =========================================================

class HLRMPipeline:
    """
    Offline compiler for HLRM knowledge store.
    """

    # -----------------------------
    # Document Parsing
    # -----------------------------

    def parse_document(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            return self._parse_pdf(file_path)

        if ext == ".docx":
            return self._parse_docx(file_path)

        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

        return ""

    def _parse_pdf(self, path: str) -> str:
        text = []
        try:
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
        except Exception as e:
            print(f"[PDF PARSE ERROR] {path}: {e}")
        return "\n".join(text)

    def _parse_docx(self, path: str) -> str:
        try:
            doc = docx.Document(path)
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as e:
            print(f"[DOCX PARSE ERROR] {path}: {e}")
            return ""

    # -----------------------------
    # Atomic Knowledge Extraction
    # -----------------------------

    def extract_atomic_knowledge(self, text: str, source: str) -> List[Dict]:
        """
        Extracts intent → answer pairs deterministically.
        Header-based with sentence fallback.
        """
        items = []
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        current_intent = None
        buffer = []

        for line in lines:
            is_header = len(line) < 80 and not line.endswith(".")

            if is_header:
                if current_intent and buffer:
                    items.append({
                        "raw_intent": current_intent,
                        "answer": " ".join(buffer),
                        "source": source
                    })
                current_intent = line.rstrip(":")
                buffer = []
            else:
                if current_intent:
                    buffer.append(line)

        if current_intent and buffer:
            items.append({
                "raw_intent": current_intent,
                "answer": " ".join(buffer),
                "source": source
            })

        return items

    # -----------------------------
    # Main Compilation Flow
    # -----------------------------

    def compile_knowledge(self, file_paths: List[str]) -> int:
        """
        Builds the JSON knowledge store.
        """
        store = {}

        for path in file_paths:
            filename = os.path.basename(path)

            # Deterministic routing
            route = "Root"
            name = filename.lower()
            if "academic" in name:
                route = "Root/Academics"
            elif "hostel" in name:
                route = "Root/Hostels"

            text = self.parse_document(path)
            if not text:
                continue

            knowledge_items = self.extract_atomic_knowledge(text, filename)

            for item in knowledge_items:
                normalized_intent = normalize(item["raw_intent"])
                if not normalized_intent:
                    continue

                h = semantic_hash(route, normalized_intent)
                key = f"{route}|{h}"

                store[key] = {
                    "answer": item["answer"],
                    "source": item["source"],
                    "original_intent": item["raw_intent"],
                    "confidence": "verified"
                }

        os.makedirs(os.path.dirname(KNOWLEDGE_STORE_PATH), exist_ok=True)
        with open(KNOWLEDGE_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2)

        return len(store)


# Singleton instance
pipeline = HLRMPipeline()
