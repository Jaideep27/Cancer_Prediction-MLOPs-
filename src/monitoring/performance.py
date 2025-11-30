"""Performance monitoring utilities."""

import time
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

from ..utils.logger import get_logger

logger = get_logger(__name__)


class PerformanceMonitor:
    """Monitor model and API performance."""

    def __init__(self):
        """Initialize performance monitor."""
        self.metrics = defaultdict(list)
        self.start_time = time.time()

    def log_prediction_time(self, duration: float) -> None:
        """
        Log prediction duration.

        Args:
            duration: Prediction duration in seconds
        """
        self.metrics["prediction_times"].append(duration)

    def log_prediction(
        self,
        prediction: int,
        confidence: float,
        actual: Optional[int] = None,
    ) -> None:
        """
        Log a prediction.

        Args:
            prediction: Predicted class
            confidence: Prediction confidence
            actual: Actual class (if available)
        """
        self.metrics["predictions"].append(
            {
                "prediction": prediction,
                "confidence": confidence,
                "actual": actual,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def log_request(self, endpoint: str, status_code: int, duration: float) -> None:
        """
        Log API request.

        Args:
            endpoint: API endpoint
            status_code: HTTP status code
            duration: Request duration
        """
        self.metrics["requests"].append(
            {
                "endpoint": endpoint,
                "status_code": status_code,
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def get_prediction_stats(self) -> Dict[str, Any]:
        """
        Get prediction statistics.

        Returns:
            Dictionary with prediction stats
        """
        if not self.metrics["prediction_times"]:
            return {}

        times = self.metrics["prediction_times"]

        return {
            "count": len(times),
            "mean_time": np.mean(times),
            "median_time": np.median(times),
            "min_time": np.min(times),
            "max_time": np.max(times),
            "p95_time": np.percentile(times, 95),
            "p99_time": np.percentile(times, 99),
        }

    def get_accuracy_stats(self) -> Dict[str, Any]:
        """
        Get accuracy statistics (if ground truth available).

        Returns:
            Dictionary with accuracy stats
        """
        predictions = self.metrics.get("predictions", [])

        if not predictions:
            return {}

        # Filter predictions with actual labels
        labeled = [p for p in predictions if p.get("actual") is not None]

        if not labeled:
            return {"message": "No ground truth labels available"}

        correct = sum(1 for p in labeled if p["prediction"] == p["actual"])
        total = len(labeled)

        # Calculate confidence stats
        confidences = [p["confidence"] for p in predictions]

        return {
            "total_predictions": len(predictions),
            "labeled_predictions": total,
            "accuracy": correct / total if total > 0 else 0,
            "mean_confidence": np.mean(confidences),
            "median_confidence": np.median(confidences),
        }

    def get_request_stats(self) -> Dict[str, Any]:
        """
        Get request statistics.

        Returns:
            Dictionary with request stats
        """
        requests = self.metrics.get("requests", [])

        if not requests:
            return {}

        durations = [r["duration"] for r in requests]
        status_codes = [r["status_code"] for r in requests]

        # Count by endpoint
        endpoints = defaultdict(int)
        for r in requests:
            endpoints[r["endpoint"]] += 1

        # Count by status code
        status_counts = defaultdict(int)
        for code in status_codes:
            status_counts[code] += 1

        return {
            "total_requests": len(requests),
            "mean_duration": np.mean(durations),
            "median_duration": np.median(durations),
            "p95_duration": np.percentile(durations, 95),
            "endpoints": dict(endpoints),
            "status_codes": dict(status_counts),
            "uptime_seconds": time.time() - self.start_time,
        }

    def get_all_stats(self) -> Dict[str, Any]:
        """
        Get all performance statistics.

        Returns:
            Dictionary with all stats
        """
        return {
            "predictions": self.get_prediction_stats(),
            "accuracy": self.get_accuracy_stats(),
            "requests": self.get_request_stats(),
            "timestamp": datetime.now().isoformat(),
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.metrics.clear()
        self.start_time = time.time()
        logger.info("Performance metrics reset")
