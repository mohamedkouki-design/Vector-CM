from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import search,counterfactual,fraud,multimodal,temporal,network,voice
import uvicorn
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Vector CM API",
    description="Self-Evolving Multimodal Credit Intelligence",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Vector CM API is running! 🚀",
        "version": "1.0.0",
        "docs": "http://localhost:8000/docs",
        "health": "http://localhost:8000/health"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(counterfactual.router, prefix="/api/v1", tags=["counterfactual"])
app.include_router(fraud.router, prefix="/api/v1", tags=["fraud"])
app.include_router(multimodal.router, prefix="/api/v1", tags=["multimodal"])
app.include_router(temporal.router, prefix="/api/v1", tags=["temporal"])
app.include_router(network.router, prefix="/api/v1", tags=["network"])
app.include_router(voice.router, prefix="/api/v1", tags=["voice"])
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Vector CM API Starting...")
    print("="*60)
    print(f"📍 API: http://localhost:8000")
    print(f"📚 Docs: http://localhost:8000/docs")
    print(f"💚 Health: http://localhost:8000/health")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")