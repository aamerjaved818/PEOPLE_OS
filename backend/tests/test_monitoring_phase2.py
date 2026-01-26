"""
Tests for Phase 2 Task 3 - Advanced Monitoring

Tests Prometheus metrics, Grafana dashboards, alert rules, and middleware.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import FastAPI, Request
from starlette.responses import Response

from backend.monitoring.prometheus_exporter import (
    PrometheusMetrics,
    MetricNamespace,
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


class TestPrometheusMetrics:
    """Tests for Prometheus metrics exporter"""

    def test_metrics_initialization(self):
        """Test metrics are properly initialized"""
        metrics = PrometheusMetrics()
        assert metrics is not None
        assert metrics.registry is not None

    def test_system_metrics_initialized(self):
        """Test system metrics are set up"""
        metrics = PrometheusMetrics()
        assert hasattr(metrics, 'system_health')
        assert hasattr(metrics, 'system_uptime_seconds')
        assert hasattr(metrics, 'system_cpu_percent')
        assert hasattr(metrics, 'system_memory_percent')
        assert hasattr(metrics, 'db_connections_active')

    def test_api_metrics_initialized(self):
        """Test API metrics are set up"""
        metrics = PrometheusMetrics()
        assert hasattr(metrics, 'api_requests_total')
        assert hasattr(metrics, 'api_latency_seconds')
        assert hasattr(metrics, 'api_errors_total')
        assert hasattr(metrics, 'api_requests_in_progress')

    def test_database_metrics_initialized(self):
        """Test database metrics are set up"""
        metrics = PrometheusMetrics()
        assert hasattr(metrics, 'db_query_latency_seconds')
        assert hasattr(metrics, 'db_queries_total')
        assert hasattr(metrics, 'db_slow_queries_total')
        assert hasattr(metrics, 'db_pool_size')
        assert hasattr(metrics, 'db_pool_checked_out')

    def test_cache_metrics_initialized(self):
        """Test cache metrics are set up"""
        metrics = PrometheusMetrics()
        assert hasattr(metrics, 'cache_hits_total')
        assert hasattr(metrics, 'cache_misses_total')
        assert hasattr(metrics, 'cache_hit_ratio')
        assert hasattr(metrics, 'cache_size_bytes')
        assert hasattr(metrics, 'cache_latency_seconds')

    def test_business_metrics_initialized(self):
        """Test business metrics are set up"""
        metrics = PrometheusMetrics()
        assert hasattr(metrics, 'employees_total')
        assert hasattr(metrics, 'departments_total')
        assert hasattr(metrics, 'active_users_total')
        assert hasattr(metrics, 'data_changes_total')
        assert hasattr(metrics, 'errors_by_type_total')

    def test_record_api_request(self):
        """Test recording API request metrics"""
        metrics = PrometheusMetrics()
        metrics.record_api_request(
            method="GET",
            endpoint="/employees",
            status=200,
            latency_seconds=0.05
        )
        # Should not raise

    def test_record_api_request_with_error(self):
        """Test recording API request with error"""
        metrics = PrometheusMetrics()
        metrics.record_api_request(
            method="POST",
            endpoint="/employees",
            status=400,
            latency_seconds=0.01,
            error_type="validation_error"
        )
        # Should not raise

    def test_record_database_query(self):
        """Test recording database query metrics"""
        metrics = PrometheusMetrics()
        metrics.record_database_query(
            operation="SELECT",
            table="employees",
            latency_seconds=0.015
        )
        # Should not raise

    def test_record_slow_query(self):
        """Test recording slow query metrics"""
        metrics = PrometheusMetrics()
        # Slow query (>0.1s)
        metrics.record_database_query(
            operation="SELECT",
            table="employees",
            latency_seconds=0.15
        )
        # Should not raise

    def test_record_cache_operation_hit(self):
        """Test recording cache hit"""
        metrics = PrometheusMetrics()
        metrics.record_cache_operation(
            cache_type="redis",
            operation="get",
            hit=True,
            latency_seconds=0.001
        )
        # Should not raise

    def test_record_cache_operation_miss(self):
        """Test recording cache miss"""
        metrics = PrometheusMetrics()
        metrics.record_cache_operation(
            cache_type="redis",
            operation="get",
            hit=False,
            latency_seconds=0.001
        )
        # Should not raise

    def test_update_cache_hit_ratio(self):
        """Test updating cache hit ratio"""
        metrics = PrometheusMetrics()
        metrics.update_cache_hit_ratio("redis", 0.85)
        # Should not raise

    def test_record_business_change(self):
        """Test recording business data changes"""
        metrics = PrometheusMetrics()
        metrics.record_business_change("employee", "create")
        metrics.record_business_change("department", "update")
        metrics.record_business_change("job_level", "delete")
        # Should not raise

    def test_record_error(self):
        """Test recording error metrics"""
        metrics = PrometheusMetrics()
        metrics.record_error("database_error")
        metrics.record_error("validation_error")
        # Should not raise

    def test_get_metrics_export(self):
        """Test getting metrics in Prometheus format"""
        metrics = PrometheusMetrics()
        result = metrics.get_metrics()
        assert isinstance(result, bytes)
        assert b"peopleOS_" in result

    def test_get_content_type(self):
        """Test getting Prometheus content type"""
        metrics = PrometheusMetrics()
        content_type = metrics.get_content_type()
        assert "text/plain" in content_type

    def test_global_metrics_instance(self):
        """Test global metrics instance"""
        metrics1 = get_metrics()
        metrics2 = get_metrics()
        assert metrics1 is metrics2

    def test_initialize_metrics(self):
        """Test metrics initialization"""
        metrics = initialize_metrics()
        assert isinstance(metrics, PrometheusMetrics)


class TestMetricsMiddleware:
    """Tests for metrics middleware"""

    @pytest.mark.asyncio
    async def test_middleware_records_request(self):
        """Test middleware records API request"""
        app = FastAPI()
        app.add_middleware(MetricsMiddleware)
        
        @app.get("/test")
        async def test_route():
            return {"status": "ok"}
        
        metrics = initialize_metrics()
        
        # Simulate request
        from starlette.testclient import TestClient
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_middleware_records_error(self):
        """Test middleware records error on exception"""
        app = FastAPI()
        app.add_middleware(MetricsMiddleware)
        
        @app.get("/error")
        async def error_route():
            raise ValueError("Test error")
        
        initialize_metrics()
        
        from starlette.testclient import TestClient
        client = TestClient(app)
        
        with pytest.raises(ValueError):
            client.get("/error")

    def test_database_metrics_recorder(self):
        """Test database metrics recorder"""
        DatabaseMetricsRecorder.record_query("SELECT", "employees", 0.05)
        DatabaseMetricsRecorder.record_error("connection_error")
        # Should not raise

    def test_cache_metrics_recorder(self):
        """Test cache metrics recorder"""
        CacheMetricsRecorder.record_operation("redis", "get", True, 0.001)
        CacheMetricsRecorder.update_hit_ratio("redis", 80, 20)
        # Should not raise

    def test_business_metrics_recorder(self):
        """Test business metrics recorder"""
        BusinessMetricsRecorder.record_employee_change("create")
        BusinessMetricsRecorder.record_department_change("update")
        BusinessMetricsRecorder.record_job_level_change("delete")
        BusinessMetricsRecorder.record_user_change("login")
        # Should not raise


class TestAlertRules:
    """Tests for alert rules configuration"""

    def test_alert_rules_structure(self):
        """Test alert rules have correct structure"""
        assert "groups" in ALERT_RULES
        assert isinstance(ALERT_RULES["groups"], list)
        assert len(ALERT_RULES["groups"]) > 0

    def test_alert_groups_defined(self):
        """Test all alert groups are defined"""
        group_names = [g["name"] for g in ALERT_RULES["groups"]]
        assert "PeopleOS System Alerts" in group_names
        assert "PeopleOS API Alerts" in group_names
        assert "PeopleOS Database Alerts" in group_names
        assert "PeopleOS Cache Alerts" in group_names
        assert "PeopleOS Business Alerts" in group_names

    def test_system_alerts_defined(self):
        """Test system alerts are defined"""
        system_group = next(g for g in ALERT_RULES["groups"] if "System" in g["name"])
        alert_names = [r["alert"] for r in system_group["rules"]]
        assert "HighCPUUsage" in alert_names
        assert "HighMemoryUsage" in alert_names
        assert "CriticalMemoryUsage" in alert_names
        assert "LowHealthScore" in alert_names

    def test_api_alerts_defined(self):
        """Test API alerts are defined"""
        api_group = next(g for g in ALERT_RULES["groups"] if "API" in g["name"])
        alert_names = [r["alert"] for r in api_group["rules"]]
        assert "HighErrorRate" in alert_names
        assert "CriticalErrorRate" in alert_names
        assert "HighAPILatency" in alert_names

    def test_database_alerts_defined(self):
        """Test database alerts are defined"""
        db_group = next(g for g in ALERT_RULES["groups"] if "Database" in g["name"])
        alert_names = [r["alert"] for r in db_group["rules"]]
        assert "SlowDatabaseQueries" in alert_names
        assert "HighQueryLatency" in alert_names

    def test_cache_alerts_defined(self):
        """Test cache alerts are defined"""
        cache_group = next(g for g in ALERT_RULES["groups"] if "Cache" in g["name"])
        alert_names = [r["alert"] for r in cache_group["rules"]]
        assert "LowCacheHitRatio" in alert_names
        assert "HighCacheLatency" in alert_names

    def test_alert_rule_structure(self):
        """Test individual alert rules have required fields"""
        for group in ALERT_RULES["groups"]:
            for rule in group["rules"]:
                assert "alert" in rule
                assert "expr" in rule
                assert "for" in rule
                assert "labels" in rule
                assert "annotations" in rule
                assert "summary" in rule["annotations"]
                assert "description" in rule["annotations"]

    def test_alert_labels_present(self):
        """Test alerts have severity and component labels"""
        for group in ALERT_RULES["groups"]:
            for rule in group["rules"]:
                labels = rule["labels"]
                assert "severity" in labels
                assert labels["severity"] in ["info", "warning", "critical"]
                assert "component" in labels

    def test_get_alert_rules_yaml(self):
        """Test converting alert rules to YAML"""
        yaml_output = get_alert_rules_yaml()
        assert isinstance(yaml_output, str)
        assert "groups:" in yaml_output
        assert "HighCPUUsage" in yaml_output

    def test_validate_alert_rules(self):
        """Test alert rules validation"""
        assert validate_alert_rules() is True

    def test_alert_expressions_syntax(self):
        """Test alert expressions contain valid PromQL"""
        for group in ALERT_RULES["groups"]:
            for rule in group["rules"]:
                expr = rule["expr"]
                assert isinstance(expr, str)
                assert len(expr) > 0
                # Check for common PromQL patterns
                assert any(x in expr for x in ["peopleOS_", "rate(", "histogram_quantile("])


class TestGrafanaDashboards:
    """Tests for Grafana dashboard configuration"""

    def test_dashboard_json_structure(self):
        """Test dashboard JSON has correct structure"""
        import json
        with open("backend/monitoring/grafana_dashboards.json") as f:
            dashboard = json.load(f)
        
        assert "panels" in dashboard
        assert "title" in dashboard
        assert "refresh" in dashboard
        assert dashboard["title"] == "PeopleOS System Overview"

    def test_dashboard_panels_exist(self):
        """Test dashboard has required panels"""
        import json
        with open("backend/monitoring/grafana_dashboards.json") as f:
            dashboard = json.load(f)
        
        panel_titles = [p.get("title", "") for p in dashboard["panels"]]
        assert "System Resources" in panel_titles
        assert "System Health Score" in panel_titles
        assert "API Request Rate" in panel_titles
        assert "API Latency Percentiles" in panel_titles
        assert "Error Rate" in panel_titles
        assert "Cache Hit Ratio" in panel_titles
        assert "Database Query Performance" in panel_titles

    def test_dashboard_has_prometheus_datasource(self):
        """Test dashboard has Prometheus datasource configured"""
        import json
        with open("backend/monitoring/grafana_dashboards.json") as f:
            dashboard = json.load(f)
        
        for panel in dashboard["panels"]:
            if panel.get("targets"):
                ds = panel.get("datasource", {})
                assert ds.get("type") == "prometheus"

    def test_dashboard_refresh_interval(self):
        """Test dashboard has appropriate refresh interval"""
        import json
        with open("backend/monitoring/grafana_dashboards.json") as f:
            dashboard = json.load(f)
        
        assert dashboard["refresh"] == "10s"

    def test_dashboard_time_range(self):
        """Test dashboard has time range configured"""
        import json
        with open("backend/monitoring/grafana_dashboards.json") as f:
            dashboard = json.load(f)
        
        assert "time" in dashboard
        assert dashboard["time"]["from"] == "now-1h"
        assert dashboard["time"]["to"] == "now"


class TestMetricsIntegration:
    """Integration tests for metrics system"""

    def test_metrics_end_to_end(self):
        """Test complete metrics flow"""
        metrics = initialize_metrics()
        
        # Record various metrics
        metrics.record_api_request("GET", "/api/employees", 200, 0.05)
        metrics.record_database_query("SELECT", "employees", 0.02)
        metrics.record_cache_operation("redis", "get", True, 0.001)
        metrics.record_business_change("employee", "create")
        
        # Export metrics
        exported = metrics.get_metrics()
        assert isinstance(exported, bytes)
        assert len(exported) > 0

    def test_multiple_operations_tracked(self):
        """Test tracking multiple operations"""
        metrics = initialize_metrics()
        
        # Record multiple requests
        for i in range(10):
            metrics.record_api_request(
                "GET",
                "/api/employees",
                200,
                0.01 * (i + 1)
            )
        
        # Should accumulate without errors
        exported = metrics.get_metrics()
        assert b"peopleOS_api_requests_total" in exported

    def test_error_tracking(self):
        """Test error tracking"""
        metrics = initialize_metrics()
        
        # Record various errors
        metrics.record_api_request("POST", "/api/employees", 400, 0.01, "validation")
        metrics.record_api_request("GET", "/api/nonexistent", 404, 0.01, "not_found")
        metrics.record_error("database_error")
        
        exported = metrics.get_metrics()
        assert b"peopleOS_api_errors_total" in exported
        assert b"peopleOS_business_errors_by_type_total" in exported

    def test_metric_labels_recorded(self):
        """Test metric labels are properly recorded"""
        metrics = PrometheusMetrics()
        
        # Record with different labels
        metrics.record_api_request("GET", "/employees", 200, 0.05)
        metrics.record_api_request("POST", "/employees", 201, 0.08)
        metrics.record_api_request("DELETE", "/employees/1", 204, 0.03)
        
        exported = metrics.get_metrics()
        assert b"GET" in exported
        assert b"POST" in exported
        assert b"DELETE" in exported


class TestMetricsPerformance:
    """Tests for metrics system performance"""

    def test_metrics_recording_speed(self):
        """Test metrics recording is fast"""
        import time
        metrics = PrometheusMetrics()
        
        start = time.time()
        for i in range(1000):
            metrics.record_api_request("GET", "/test", 200, 0.01)
        elapsed = time.time() - start
        
        # Should complete 1000 recordings in < 1 second
        assert elapsed < 1.0

    def test_concurrent_metrics_recording(self):
        """Test concurrent metrics recording"""
        import concurrent.futures
        metrics = PrometheusMetrics()
        
        def record_metric():
            metrics.record_api_request("GET", "/test", 200, 0.01)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(record_metric) for _ in range(100)]
            for f in concurrent.futures.as_completed(futures):
                assert f.result() is None


class TestMetricsNamespaces:
    """Tests for metric namespaces"""

    def test_namespace_enum_values(self):
        """Test metric namespace enum values"""
        assert MetricNamespace.SYSTEM == "peopleOS_system"
        assert MetricNamespace.API == "peopleOS_api"
        assert MetricNamespace.DATABASE == "peopleOS_database"
        assert MetricNamespace.CACHE == "peopleOS_cache"
        assert MetricNamespace.BUSINESS == "peopleOS_business"

    def test_metric_names_use_namespace(self):
        """Test metric names include namespace prefix"""
        metrics = PrometheusMetrics()
        exported = metrics.get_metrics()
        
        # Check for namespace prefixes in exported metrics
        assert b"peopleOS_system_" in exported
        assert b"peopleOS_api_" in exported
        assert b"peopleOS_database_" in exported
        assert b"peopleOS_cache_" in exported
        assert b"peopleOS_business_" in exported


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
