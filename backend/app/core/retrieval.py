import json
import os
import time
from typing import Dict, Optional

from .config import KNOWLEDGE_STORE_PATH
from .pipeline import normalize, semantic_hash


class HLRMRetrieval:
    """
    Runtime retrieval engine for HLRM.
    Performs deterministic O(1) hash-based lookup.
    """

    def __init__(self):
        self.knowledge_map: Dict = {}
        self.load_knowledge()

    def load_knowledge(self) -> None:
        """Load the compiled knowledge store into memory."""
        if os.path.exists(KNOWLEDGE_STORE_PATH):
            with open(KNOWLEDGE_STORE_PATH, "r", encoding="utf-8") as f:
                self.knowledge_map = json.load(f)
        else:
            self.knowledge_map = {}

        print(f"Loaded {len(self.knowledge_map)} items into memory.")

    def query(self, user_query: str) -> Dict:
        """
        Deterministic retrieval pipeline:
        1. Normalize query
        2. Generate semantic hash
        3. Probe known routes (constant, small set)
        4. Return verified answer or safe fallback
        """
        start = time.perf_counter()

        normalized_query = normalize(user_query)

        # Fixed, small route set → effectively O(1)
        possible_routes = [
            "Root",
            "Root/Academics",
            "Root/Hostels",
            "Root/Administration"
        ]

        for route in possible_routes:
            h = semantic_hash(route, normalized_query)
            key = f"{route}|{h}"

            if key in self.knowledge_map:
                latency_ms = (time.perf_counter() - start) * 1000
                record = self.knowledge_map[key]

                return {
                    "found": True,
                    "answer": record["answer"],
                    "source": record["source"],
                    "domain": route,
                    "latency_ms": round(latency_ms, 3),
                    "confidence": record.get("confidence", "verified")
                }

        latency_ms = (time.perf_counter() - start) * 1000

        return {
            "found": False,
            "answer": "I'm sorry, I don't have verified knowledge about that yet.",
            "latency_ms": round(latency_ms, 3)
        }


# Singleton retriever instance
retriever = HLRMRetrieval()
