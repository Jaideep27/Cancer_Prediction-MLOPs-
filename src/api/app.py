"""FastAPI application for Cancer Prediction API."""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.pipelines.inference_pipeline import InferencePipeline
from src.utils.config import get_config, get_env
from src.utils.logger import get_logger
from src.api.middleware import RequestLoggingMiddleware
from src.api.schemas import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    ErrorResponse,
    HealthResponse,
    PredictionRequest,
    PredictionResponse,
)

# Initialize logger
logger = get_logger(__name__)

# Load deployment configuration
deployment_config = get_config("deployment_config")
api_config = deployment_config.get("api", {})

# Initialize FastAPI app
app = FastAPI(
    title=api_config.get("title", "Cancer Prediction API"),
    description=api_config.get("description", "MLOps API for breast cancer prediction"),
    version=api_config.get("version", "1.0.0"),
)

# CORS middleware
cors_config = api_config.get("cors", {})
if cors_config.get("enabled", True):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.get("allow_origins", ["*"]),
        allow_credentials=cors_config.get("allow_credentials", True),
        allow_methods=cors_config.get("allow_methods", ["*"]),
        allow_headers=cors_config.get("allow_headers", ["*"]),
    )

# Request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Global inference pipeline (loaded once at startup)
inference_pipeline: Optional[InferencePipeline] = None


@app.on_event("startup")
async def startup_event():
    """Initialize the inference pipeline on startup."""
    global inference_pipeline

    try:
        model_serving_config = deployment_config.get("model_serving", {})
        model_name = get_env("DEFAULT_MODEL") or model_serving_config.get("model_name", "hybrid_ensemble")
        model_version = get_env("MODEL_VERSION") or model_serving_config.get("model_version", "latest")

        logger.info(f"Loading model: {model_name} v{model_version}")

        inference_pipeline = InferencePipeline(
            model_name=model_name,
            model_version=model_version,
        )

        logger.info("Inference pipeline initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize inference pipeline: {str(e)}")
        # Don't raise - allow API to start but endpoints will return errors


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Cancer Prediction API",
        "version": api_config.get("version", "1.0.0"),
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "batch_predict": "/batch_predict",
            "docs": "/docs",
        },
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    if inference_pipeline is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return HealthResponse(
        status="healthy",
        model_name=inference_pipeline.model_name,
        model_version=inference_pipeline.model_version,
        timestamp=datetime.now().isoformat(),
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict(request: PredictionRequest):
    """
    Make a single prediction.

    Args:
        request: Prediction request with features

    Returns:
        Prediction result with diagnosis and confidence
    """
    if inference_pipeline is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Convert Pydantic model to dict
        features_dict = request.features.model_dump(by_alias=True)

        # Make prediction
        result = inference_pipeline.predict_single(
            features=features_dict,
            return_proba=request.return_probabilities,
        )

        return PredictionResponse(**result)

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/batch_predict", response_model=BatchPredictionResponse, tags=["Prediction"])
async def batch_predict(request: BatchPredictionRequest):
    """
    Make batch predictions.

    Args:
        request: Batch prediction request with multiple feature sets

    Returns:
        Batch prediction results
    """
    if inference_pipeline is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Convert Pydantic models to list of dicts
        features_list = [f.model_dump(by_alias=True) for f in request.features]

        # Make predictions
        result = inference_pipeline.predict_with_confidence(features_list)

        response = {
            "predictions": result["predictions"].tolist(),
            "count": len(result["predictions"]),
        }

        if request.return_probabilities:
            probabilities = [
                {
                    "benign": float(prob[0]),
                    "malignant": float(prob[1]),
                }
                for prob in result["probabilities"]
            ]
            response["probabilities"] = probabilities

        return BatchPredictionResponse(**response)

    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


def main():
    """Run the FastAPI application."""
    host = get_env("API_HOST") or api_config.get("host", "0.0.0.0")
    port = int(get_env("API_PORT") or api_config.get("port", 8000))
    workers = int(get_env("API_WORKERS") or api_config.get("workers", 4))
    reload = get_env("API_RELOAD") == "True" or api_config.get("reload", False)

    logger.info(f"Starting API server on {host}:{port}")

    uvicorn.run(
        "src.api.app:app",
        host=host,
        port=port,
        workers=workers if not reload else 1,
        reload=reload,
        log_level=api_config.get("log_level", "info"),
    )


if __name__ == "__main__":
    main()
