"""
peopleOS eBusiness Suite Monitoring Module

Provides comprehensive monitoring, metrics collection, and alerting infrastructure.
"""

from backend.monitoring.prometheus_exporter import (
    PrometheusMetrics,
    get_metrics,
    initialize_metrics,
)

from backend.monitoring.metrics_middleware import (
    MetricsMiddleware,
    DatabaseMetricsRecorder,
    CacheMetricsRecorder,
    BusinessMetricsRecorder,
)

from backend.monitoring.alert_rules import (
    ALERT_RULES,
    get_alert_rules_yaml,
    validate_alert_rules,
)

__all__ = [
    "PrometheusMetrics",
    "get_metrics",
    "initialize_metrics",
    "MetricsMiddleware",
    "DatabaseMetricsRecorder",
    "CacheMetricsRecorder",
    "BusinessMetricsRecorder",
    "ALERT_RULES",
    "get_alert_rules_yaml",
    "validate_alert_rules",
]
