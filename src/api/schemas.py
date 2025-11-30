"""Pydantic schemas for API request/response validation."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


class FeatureInput(BaseModel):
    """Individual feature input for prediction."""

    radius_mean: float = Field(..., description="Mean radius")
    texture_mean: float = Field(..., description="Mean texture")
    perimeter_mean: float = Field(..., description="Mean perimeter")
    area_mean: float = Field(..., description="Mean area")
    smoothness_mean: float = Field(..., description="Mean smoothness")
    compactness_mean: float = Field(..., description="Mean compactness")
    concavity_mean: float = Field(..., description="Mean concavity")
    concave_points_mean: float = Field(alias="concave points_mean", description="Mean concave points")
    symmetry_mean: float = Field(..., description="Mean symmetry")
    fractal_dimension_mean: float = Field(..., description="Mean fractal dimension")

    radius_se: float = Field(..., description="Radius standard error")
    texture_se: float = Field(..., description="Texture standard error")
    perimeter_se: float = Field(..., description="Perimeter standard error")
    area_se: float = Field(..., description="Area standard error")
    smoothness_se: float = Field(..., description="Smoothness standard error")
    compactness_se: float = Field(..., description="Compactness standard error")
    concavity_se: float = Field(..., description="Concavity standard error")
    concave_points_se: float = Field(alias="concave points_se", description="Concave points standard error")
    symmetry_se: float = Field(..., description="Symmetry standard error")
    fractal_dimension_se: float = Field(..., description="Fractal dimension standard error")

    radius_worst: float = Field(..., description="Worst radius")
    texture_worst: float = Field(..., description="Worst texture")
    perimeter_worst: float = Field(..., description="Worst perimeter")
    area_worst: float = Field(..., description="Worst area")
    smoothness_worst: float = Field(..., description="Worst smoothness")
    compactness_worst: float = Field(..., description="Worst compactness")
    concavity_worst: float = Field(..., description="Worst concavity")
    concave_points_worst: float = Field(alias="concave points_worst", description="Worst concave points")
    symmetry_worst: float = Field(..., description="Worst symmetry")
    fractal_dimension_worst: float = Field(..., description="Worst fractal dimension")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "radius_mean": 17.99,
                "texture_mean": 10.38,
                "perimeter_mean": 122.8,
                "area_mean": 1001.0,
                "smoothness_mean": 0.1184,
                "compactness_mean": 0.2776,
                "concavity_mean": 0.3001,
                "concave points_mean": 0.1471,
                "symmetry_mean": 0.2419,
                "fractal_dimension_mean": 0.07871,
                "radius_se": 1.095,
                "texture_se": 0.9053,
                "perimeter_se": 8.589,
                "area_se": 153.4,
                "smoothness_se": 0.006399,
                "compactness_se": 0.04904,
                "concavity_se": 0.05373,
                "concave points_se": 0.01587,
                "symmetry_se": 0.03003,
                "fractal_dimension_se": 0.006193,
                "radius_worst": 25.38,
                "texture_worst": 17.33,
                "perimeter_worst": 184.6,
                "area_worst": 2019.0,
                "smoothness_worst": 0.1622,
                "compactness_worst": 0.6656,
                "concavity_worst": 0.7119,
                "concave points_worst": 0.2654,
                "symmetry_worst": 0.4601,
                "fractal_dimension_worst": 0.1189,
            }
        }


class PredictionRequest(BaseModel):
    """Request schema for single prediction."""

    features: FeatureInput
    return_probabilities: bool = Field(default=True, description="Whether to return probabilities")


class BatchPredictionRequest(BaseModel):
    """Request schema for batch predictions."""

    features: List[FeatureInput]
    return_probabilities: bool = Field(default=True, description="Whether to return probabilities")


class PredictionResponse(BaseModel):
    """Response schema for single prediction."""

    prediction: int = Field(..., description="Predicted class (0=Benign, 1=Malignant)")
    diagnosis: str = Field(..., description="Diagnosis label")
    confidence: float = Field(..., description="Prediction confidence")
    probability_benign: Optional[float] = Field(None, description="Probability of benign diagnosis")
    probability_malignant: Optional[float] = Field(None, description="Probability of malignant diagnosis")


class BatchPredictionResponse(BaseModel):
    """Response schema for batch predictions."""

    predictions: List[int] = Field(..., description="List of predicted classes")
    count: int = Field(..., description="Number of predictions")
    probabilities: Optional[List[Dict[str, float]]] = Field(None, description="Prediction probabilities")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    model_name: str = Field(..., description="Loaded model name")
    model_version: str = Field(..., description="Model version")
    timestamp: str = Field(..., description="Current timestamp")


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
