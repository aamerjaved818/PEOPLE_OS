"""
Prometheus alert rules for peopleOS eBusiness Suite

Defines threshold-based alerts for system, performance, and business metrics.
"""

ALERT_RULES = {
    "groups": [
        {
            "name": "PeopleOS System Alerts",
            "interval": "30s",
            "rules": [
                {
                    "alert": "HighCPUUsage",
                    "expr": "peopleOS_system_cpu_percent > 80",
                    "for": "5m",
                    "labels": {
                        "severity": "warning",
                        "component": "system"
                    },
                    "annotations": {
                        "summary": "High CPU Usage Detected",
                        "description": "CPU usage is above 80% for more than 5 minutes. Current: {{ $value }}%"
                    }
                },
                {
                    "alert": "HighMemoryUsage",
                    "expr": "peopleOS_system_memory_percent > 85",
                    "for": "5m",
                    "labels": {
                        "severity": "warning",
                        "component": "system"
                    },
                    "annotations": {
                        "summary": "High Memory Usage Detected",
                        "description": "Memory usage is above 85% for more than 5 minutes. Current: {{ $value }}%"
                    }
                },
                {
                    "alert": "CriticalMemoryUsage",
                    "expr": "peopleOS_system_memory_percent > 95",
                    "for": "2m",
                    "labels": {
                        "severity": "critical",
                        "component": "system"
                    },
                    "annotations": {
                        "summary": "Critical Memory Usage",
                        "description": "Memory usage exceeds 95%. Immediate action required. Current: {{ $value }}%"
                    }
                },
                {
                    "alert": "LowHealthScore",
                    "expr": "peopleOS_system_health_score < 3.0",
                    "for": "5m",
                    "labels": {
                        "severity": "critical",
                        "component": "system"
                    },
                    "annotations": {
                        "summary": "System Health Score Critical",
                        "description": "System health score below 3.0. Current score: {{ $value }}/5.0"
                    }
                },
                {
                    "alert": "HighDatabaseConnections",
                    "expr": "peopleOS_system_db_connections_active > 80",
                    "for": "5m",
                    "labels": {
                        "severity": "warning",
                        "component": "database"
                    },
                    "annotations": {
                        "summary": "High Database Connection Count",
                        "description": "Active database connections exceed 80. Current: {{ $value }}"
                    }
                }
            ]
        },
        {
            "name": "PeopleOS API Alerts",
            "interval": "30s",
            "rules": [
                {
                    "alert": "HighErrorRate",
                    "expr": "rate(peopleOS_api_errors_total[5m]) > 0.05",
                    "for": "5m",
                    "labels": {
                        "severity": "warning",
                        "component": "api"
                    },
                    "annotations": {
                        "summary": "High API Error Rate",
                        "description": "API error rate exceeds 5% over last 5 minutes. Current rate: {{ $value }} errors/sec"
                    }
                },
                {
                    "alert": "CriticalErrorRate",
                    "expr": "rate(peopleOS_api_errors_total[5m]) > 0.2",
                    "for": "2m",
                    "labels": {
                        "severity": "critical",
                        "component": "api"
                    },
                    "annotations": {
                        "summary": "Critical API Error Rate",
                        "description": "API error rate exceeds 20% (critical threshold). Current rate: {{ $value }} errors/sec"
                    }
                },
                {
                    "alert": "HighAPILatency",
                    "expr": "histogram_quantile(0.95, rate(peopleOS_api_latency_seconds_bucket[5m])) > 1.0",
                    "for": "5m",
                    "labels": {
                        "severity": "warning",
                        "component": "api"
                    },
                    "annotations": {
                        "summary": "High API Latency",
                        "description": "p95 API latency exceeds 1 second. Current p95: {{ $value }}s"
                    }
                },
                {
                    "alert": "TooManyInflightRequests",
                    "expr": "peopleOS_api_requests_in_progress > 100",
                    "for": "5m",
                    "labels": {
                        "severity": "warning",
                        "component": "api"
                    },
                    "annotations": {
                        "summary": "Too Many In-Flight Requests",
                        "description": "Number of in-flight API requests exceeds 100. Current: {{ $value }}"
                    }
                }
            ]
        },
        {
            "name": "PeopleOS Database Alerts",
            "interval": "30s",
            "rules": [
                {
                    "alert": "SlowDatabaseQueries",
                    "expr": "rate(peopleOS_database_slow_queries_total[5m]) > 1",
                    "for": "5m",
                    "labels": {
                        "severity": "warning",
                        "component": "database"
                    },
                    "annotations": {
                        "summary": "Slow Database Queries Detected",
                        "description": "Database queries exceeding 100ms detected. Rate: {{ $value }} queries/sec"
                    }
                },
                {
                    "alert": "HighQueryLatency",
                    "expr": "histogram_quantile(0.99, rate(peopleOS_database_query_latency_seconds_bucket[5m])) > 0.5",
                    "for": "5m",
                    "labels": {
                        "severity": "warning",
                        "component": "database"
                    },
                    "annotations": {
                        "summary": "High Database Query Latency",
                        "description": "p99 query latency exceeds 500ms. Current p99: {{ $value }}s"
                    }
                },
                {
                    "alert": "DatabaseConnectionPoolExhausted",
                    "expr": "peopleOS_database_pool_checked_out / peopleOS_database_pool_size > 0.9",
                    "for": "5m",
                    "labels": {
                        "severity": "critical",
                        "component": "database"
                    },
                    "annotations": {
                        "summary": "Database Connection Pool Near Exhaustion",
                        "description": "More than 90% of database connections are in use. Utilization: {{ $value | humanizePercentage }}"
                    }
                }
            ]
        },
        {
            "name": "PeopleOS Cache Alerts",
            "interval": "30s",
            "rules": [
                {
                    "alert": "LowCacheHitRatio",
                    "expr": "peopleOS_cache_hit_ratio < 0.6",
                    "for": "10m",
                    "labels": {
                        "severity": "warning",
                        "component": "cache"
                    },
                    "annotations": {
                        "summary": "Cache Hit Ratio Below Target",
                        "description": "Cache hit ratio below 60% target. Current ratio: {{ $value | humanizePercentage }}"
                    }
                },
                {
                    "alert": "CriticalLowCacheHitRatio",
                    "expr": "peopleOS_cache_hit_ratio < 0.3",
                    "for": "5m",
                    "labels": {
                        "severity": "critical",
                        "component": "cache"
                    },
                    "annotations": {
                        "summary": "Critical Cache Hit Ratio",
                        "description": "Cache hit ratio critically low at {{ $value | humanizePercentage }}. Cache may be ineffective."
                    }
                },
                {
                    "alert": "HighCacheLatency",
                    "expr": "histogram_quantile(0.99, rate(peopleOS_cache_latency_seconds_bucket[5m])) > 0.01",
                    "for": "5m",
                    "labels": {
                        "severity": "warning",
                        "component": "cache"
                    },
                    "annotations": {
                        "summary": "High Cache Operation Latency",
                        "description": "p99 cache latency exceeds 10ms. Current p99: {{ $value }}s"
                    }
                }
            ]
        },
        {
            "name": "PeopleOS Business Alerts",
            "interval": "30s",
            "rules": [
                {
                    "alert": "HighErrorCount",
                    "expr": "rate(peopleOS_business_errors_by_type_total[5m]) > 10",
                    "for": "5m",
                    "labels": {
                        "severity": "warning",
                        "component": "business"
                    },
                    "annotations": {
                        "summary": "High Business Logic Error Rate",
                        "description": "Business logic errors exceeding 10 per second. Current rate: {{ $value }} errors/sec"
                    }
                },
                {
                    "alert": "DataModificationAnomaly",
                    "expr": "rate(peopleOS_business_data_changes_total[5m]) > 1000",
                    "for": "2m",
                    "labels": {
                        "severity": "warning",
                        "component": "business"
                    },
                    "annotations": {
                        "summary": "Unusual Data Modification Rate",
                        "description": "Data modification rate exceeds normal threshold. Current rate: {{ $value }} changes/sec"
                    }
                }
            ]
        }
    ]
}


def get_alert_rules_yaml() -> str:
    """Convert alert rules to Prometheus YAML format"""
    import yaml
    return yaml.dump(ALERT_RULES, default_flow_style=False, sort_keys=False)


def validate_alert_rules() -> bool:
    """Validate alert rules configuration"""
    try:
        assert "groups" in ALERT_RULES
        for group in ALERT_RULES["groups"]:
            assert "name" in group
            assert "rules" in group
            for rule in group["rules"]:
                assert "alert" in rule
                assert "expr" in rule
                assert "labels" in rule
                assert "annotations" in rule
        return True
    except AssertionError:
        return False
