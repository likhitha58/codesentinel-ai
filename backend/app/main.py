
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router


app = FastAPI(
    title="CodeSentinel AI",
    description=(
        "Architecture-agnostic repository security, "
        "code quality, and coding-gap auditing platform."
    ),
    version="1.0.0",
)

# Allow frontend dev server and production origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Register repository audit endpoints.
app.include_router(router)


@app.get("/", tags=["General"])
def root():
    return {
        "name": "CodeSentinel AI",
        "version": "1.0.0",
        "description": "Repository Security and Quality Auditing Agent",
        "status": "running",
        "documentation": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "CodeSentinel AI API",
    }
