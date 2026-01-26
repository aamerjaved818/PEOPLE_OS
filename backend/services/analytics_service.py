from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from backend.domains.hcm import models as hcm_models
from backend.domains.core import models as core_models
from backend.services.analytics_calculator import AnalyticsCalculator
from typing import Dict, List, Any

class AnalyticsService:
    @staticmethod
    def get_dashboard_summary(db: Session, organization_id: str) -> Dict[str, Any]:
        """Provides high-level summary metrics for the analytics dashboard."""
        # Use real calculations from AnalyticsCalculator
        return AnalyticsCalculator.calculate_dashboard_metrics(db, organization_id)

    @staticmethod
    def get_headcount_trends(db: Session, organization_id: str) -> List[Dict[str, Any]]:
        """Calculates monthly headcount growth trends."""
        return AnalyticsCalculator.calculate_headcount_trends(db, organization_id, 6)

    @staticmethod
    def get_recruitment_funnel(db: Session, organization_id: str) -> List[Dict[str, Any]]:
        """Provides candidate counts by recruitment stage."""
        return AnalyticsCalculator.calculate_recruitment_funnel(db, organization_id)

    @staticmethod
    def get_engagement_data(db: Session, organization_id: str) -> List[Dict[str, Any]]:
        """Get engagement metrics - Note: Requires engagement module backend"""
        # For now, returns mock data as engagement module doesn't exist
        # TODO: Integrate with engagement/survey module when available
        return [
            {"name": "Mon", "engagement": 65, "productivity": 80, "sentiment": 72},
            {"name": "Tue", "engagement": 72, "productivity": 85, "sentiment": 78},
            {"name": "Wed", "engagement": 85, "productivity": 82, "sentiment": 84},
            {"name": "Thu", "engagement": 88, "productivity": 90, "sentiment": 82},
            {"name": "Fri", "engagement": 78, "productivity": 75, "sentiment": 80},
        ]
