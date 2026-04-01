from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="HLRM Intelligent Query System",
    description="Deterministic O(1) Retrieval System without Embeddings",
    version="1.0.0"
)

# CORS Setup
origins = ["*"]  # For development, allow all. In production, restrict this.

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "HLRM System Online", "version": "1.0.0"}

from app.api.endpoints import router as api_router
app.include_router(api_router)
