"""
Resume Agent — FastAPI entry point.

Run with:
    cd src
    uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from api.routes import router

app = FastAPI(
    title="Resume Agent API",
    description="AI-powered tailored resume builder with ATS optimization",
    version="1.0.0",
)

# CORS — allow Streamlit and local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router)


@app.on_event("startup")
async def startup():
    logger.info("Resume Agent API starting up")


@app.on_event("shutdown")
async def shutdown():
    logger.info("Resume Agent API shutting down")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
