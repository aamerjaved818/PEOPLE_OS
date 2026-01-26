"""
Application metrics middleware for FastAPI

Automatically records metrics for all API requests, database operations, and cache access.
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from backend.monitoring.prometheus_exporter import get_metrics


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to record metrics for all API requests"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Record metrics for request"""
        metrics = get_metrics()
        
        # Record request start
        start_time = time.time()
        metrics.api_requests_in_progress.inc()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate latency
            latency = time.time() - start_time
            
            # Record metrics
            method = request.method
            endpoint = request.url.path
            status = response.status_code
            error_type = None
            
            # Determine error type if applicable
            if status >= 400:
                if status >= 500:
                    error_type = "server_error"
                elif status == 404:
                    error_type = "not_found"
                elif status == 401:
                    error_type = "unauthorized"
                elif status == 403:
                    error_type = "forbidden"
                else:
                    error_type = "client_error"
            
            metrics.record_api_request(
                method=method,
                endpoint=endpoint,
                status=status,
                latency_seconds=latency,
                error_type=error_type
            )
            
            return response
            
        except Exception as exc:
            # Record error
            latency = time.time() - start_time
            metrics.record_api_request(
                method=request.method,
                endpoint=request.url.path,
                status=500,
                latency_seconds=latency,
                error_type=type(exc).__name__
            )
            metrics.record_error("request_exception")
            raise
            
        finally:
            # Always decrement request counter
            metrics.api_requests_in_progress.dec()


class DatabaseMetricsRecorder:
    """Helper class to record database metrics"""

    @staticmethod
    def record_query(operation: str, table: str, latency_seconds: float):
        """Record database query"""
        metrics = get_metrics()
        metrics.record_database_query(
            operation=operation,
            table=table,
            latency_seconds=latency_seconds
        )

    @staticmethod
    def record_error(error_type: str):
        """Record database error"""
        metrics = get_metrics()
        metrics.record_error(f"db_{error_type}")


class CacheMetricsRecorder:
    """Helper class to record cache metrics"""

    @staticmethod
    def record_operation(
        cache_type: str,
        operation: str,
        hit: bool,
        latency_seconds: float
    ):
        """Record cache operation"""
        metrics = get_metrics()
        metrics.record_cache_operation(
            cache_type=cache_type,
            operation=operation,
            hit=hit,
            latency_seconds=latency_seconds
        )

    @staticmethod
    def update_hit_ratio(cache_type: str, hits: int, misses: int):
        """Update cache hit ratio"""
        metrics = get_metrics()
        total = hits + misses
        if total > 0:
            ratio = hits / total
            metrics.update_cache_hit_ratio(cache_type, ratio)


class BusinessMetricsRecorder:
    """Helper class to record business metrics"""

    @staticmethod
    def record_employee_change(operation: str):
        """Record employee data change"""
        metrics = get_metrics()
        metrics.record_business_change("employee", operation)

    @staticmethod
    def record_department_change(operation: str):
        """Record department data change"""
        metrics = get_metrics()
        metrics.record_business_change("department", operation)

    @staticmethod
    def record_job_level_change(operation: str):
        """Record job level data change"""
        metrics = get_metrics()
        metrics.record_business_change("job_level", operation)

    @staticmethod
    def record_user_change(operation: str):
        """Record user data change"""
        metrics = get_metrics()
        metrics.record_business_change("user", operation)
