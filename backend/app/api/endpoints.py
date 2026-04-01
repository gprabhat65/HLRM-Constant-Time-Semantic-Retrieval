from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from pydantic import BaseModel
import shutil
import os
from ..core.config import DATA_DIR
from ..core.pipeline import pipeline
from ..core.retrieval import retriever

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    domain: str = "Unknown"
    source: str = "N/A"
    latency: float
    found: bool

@router.post("/query", response_model=QueryResponse)
async def query_knowledge(request: QueryRequest):
    result = retriever.query(request.query)
    return QueryResponse(
        answer=result["answer"],
        domain=result.get("domain", "Unknown"),
        source=result.get("source", "N/A"),
        latency=result["latency_ms"],
        found=result["found"]
    )

@router.post("/admin/upload")
async def upload_document(file: UploadFile = File(...)):
    file_path = os.path.join(DATA_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": f"File {file.filename} uploaded successfully"}

@router.post("/admin/compile")
async def compile_knowledge():
    # Gather all files in data dir
    files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, f)) and not f.endswith('.json') and not f.endswith('README.txt')]
    
    count = pipeline.compile_knowledge(files)
    retriever.load_knowledge() # Reload immediately
    return {"status": "success", "entries_compiled": count}

@router.post("/admin/reload")
async def reload_store():
    retriever.load_knowledge()
    return {"status": "reloaded", "entries": len(retriever.knowledge_map)}

@router.get("/admin/status")
async def get_status():
    files = [f for f in os.listdir(DATA_DIR) if not f.endswith('.json')]
    entries = len(retriever.knowledge_map)
    return {
        "files_present": len(files),
        "knowledge_entries": entries,
        "files": files
    }
