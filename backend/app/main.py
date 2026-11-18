
from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="CodeSentinel AI",
    description=(
        "Architecture-agnostic repository security, "
        "code quality, and coding-gap auditing platform."
    ),
    version="1.0.0",
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
