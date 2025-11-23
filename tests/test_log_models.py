"""
Tests for log models (AuditLog, CollectionLog, ComplianceLog)
"""

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.storage.models import (
    ActionType,
    AuditLog,
    Base,
    CollectionLog,
    CollectionStatus,
    ComplianceEventType,
    ComplianceLog,
    ComplianceRegulation,
)
from src.storage.models.enums import CountryCode, DataSourceType


@pytest.fixture
def db_session():
    """Create in-memory database session for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestAuditLog:
    """Tests for AuditLog model."""

    def test_create_audit_log(self, db_session: Session):
        """Test creating an audit log entry."""
        log = AuditLog(
            action_type=ActionType.CREATE,
            user_id=1,
            username="test_user",
            resource_type="Video",
            resource_id="123",
            description="Created new video record",
            ip_address="192.168.1.1",
            status="SUCCESS",
            execution_time_ms=150,
        )

        db_session.add(log)
        db_session.commit()

        assert log.id is not None
        assert log.action_type == ActionType.CREATE
        assert log.username == "test_user"
        assert log.status == "SUCCESS"
        assert log.created_at is not None
        assert log.updated_at is not None

    def test_audit_log_with_error(self, db_session: Session):
        """Test creating an audit log with error."""
        log = AuditLog(
            action_type=ActionType.DELETE,
            user_id=2,
            username="admin",
            resource_type="Hashtag",
            resource_id="456",
            description="Failed to delete hashtag",
            status="FAILED",
            error_message="Database constraint violation",
        )

        db_session.add(log)
        db_session.commit()

        assert log.id is not None
        assert log.status == "FAILED"
        assert log.error_message is not None

    def test_query_audit_logs_by_action(self, db_session: Session):
        """Test querying audit logs by action type."""
        logs = [
            AuditLog(
                action_type=ActionType.CREATE,
                description="Create action 1",
                status="SUCCESS",
            ),
            AuditLog(
                action_type=ActionType.CREATE,
                description="Create action 2",
                status="SUCCESS",
            ),
            AuditLog(
                action_type=ActionType.UPDATE, description="Update action", status="SUCCESS"
            ),
        ]

        db_session.add_all(logs)
        db_session.commit()

        create_logs = (
            db_session.query(AuditLog).filter(AuditLog.action_type == ActionType.CREATE).all()
        )

        assert len(create_logs) == 2


class TestCollectionLog:
    """Tests for CollectionLog model."""

    def test_create_collection_log(self, db_session: Session):
        """Test creating a collection log entry."""
        log = CollectionLog(
            country_code=CountryCode.US,
            data_source=DataSourceType.OFFICIAL_API,
            status=CollectionStatus.SUCCESS,
            items_collected=150,
            items_processed=150,
            items_failed=0,
            api_calls_made=5,
            execution_time_seconds=12.5,
            completed_at=datetime.now(),
        )

        db_session.add(log)
        db_session.commit()

        assert log.id is not None
        assert log.country_code == CountryCode.US
        assert log.data_source == DataSourceType.OFFICIAL_API
        assert log.status == CollectionStatus.SUCCESS
        assert log.items_collected == 150

    def test_collection_log_with_failure(self, db_session: Session):
        """Test creating a collection log with failure."""
        log = CollectionLog(
            country_code=CountryCode.BR,
            data_source=DataSourceType.PLAYWRIGHT_SCRAPER,
            status=CollectionStatus.FAILED,
            items_collected=0,
            items_processed=0,
            items_failed=0,
            error_message="Connection timeout",
            error_type="NetworkError",
            retry_count=3,
        )

        db_session.add(log)
        db_session.commit()

        assert log.id is not None
        assert log.status == CollectionStatus.FAILED
        assert log.error_message is not None
        assert log.retry_count == 3

    def test_collection_log_rate_limit(self, db_session: Session):
        """Test collection log with rate limit hit."""
        log = CollectionLog(
            country_code=CountryCode.MX,
            data_source=DataSourceType.OFFICIAL_API,
            status=CollectionStatus.RATE_LIMITED,
            items_collected=50,
            items_processed=50,
            api_calls_made=100,
            rate_limit_hit=True,
        )

        db_session.add(log)
        db_session.commit()

        assert log.id is not None
        assert log.rate_limit_hit is True
        assert log.status == CollectionStatus.RATE_LIMITED


class TestComplianceLog:
    """Tests for ComplianceLog model."""

    def test_create_compliance_log(self, db_session: Session):
        """Test creating a compliance log entry."""
        log = ComplianceLog(
            regulation=ComplianceRegulation.LGPD,
            event_type=ComplianceEventType.DATA_ACCESS,
            user_id=10,
            user_email="user@example.com",
            description="User accessed personal data",
            risk_level="LOW",
            action_required=False,
            action_taken=True,
        )

        db_session.add(log)
        db_session.commit()

        assert log.id is not None
        assert log.regulation == ComplianceRegulation.LGPD
        assert log.event_type == ComplianceEventType.DATA_ACCESS
        assert log.risk_level == "LOW"

    def test_compliance_log_high_risk(self, db_session: Session):
        """Test compliance log with high risk."""
        log = ComplianceLog(
            regulation=ComplianceRegulation.GDPR,
            event_type=ComplianceEventType.DATA_BREACH,
            description="Unauthorized access detected",
            risk_level="HIGH",
            action_required=True,
            action_taken=False,
            compliance_officer="John Doe",
        )

        db_session.add(log)
        db_session.commit()

        assert log.id is not None
        assert log.risk_level == "HIGH"
        assert log.action_required is True
        assert log.action_taken is False

    def test_query_compliance_logs_by_regulation(self, db_session: Session):
        """Test querying compliance logs by regulation."""
        logs = [
            ComplianceLog(
                regulation=ComplianceRegulation.LGPD,
                event_type=ComplianceEventType.DATA_ACCESS,
                description="LGPD event 1",
                risk_level="LOW",
            ),
            ComplianceLog(
                regulation=ComplianceRegulation.LGPD,
                event_type=ComplianceEventType.DATA_EXPORT,
                description="LGPD event 2",
                risk_level="LOW",
            ),
            ComplianceLog(
                regulation=ComplianceRegulation.GDPR,
                event_type=ComplianceEventType.CONSENT_GIVEN,
                description="GDPR event",
                risk_level="LOW",
            ),
        ]

        db_session.add_all(logs)
        db_session.commit()

        lgpd_logs = (
            db_session.query(ComplianceLog)
            .filter(ComplianceLog.regulation == ComplianceRegulation.LGPD)
            .all()
        )

        assert len(lgpd_logs) == 2

    def test_compliance_log_with_action_tracking(self, db_session: Session):
        """Test compliance log with action tracking."""
        log = ComplianceLog(
            regulation=ComplianceRegulation.CCPA,
            event_type=ComplianceEventType.PRIVACY_REQUEST,
            user_id=20,
            user_email="privacy@example.com",
            description="User requested data deletion",
            action_required=True,
            action_taken=True,
            action_details="Data deleted from all systems",
            compliance_officer="Jane Smith",
            reviewed_at=datetime.now(),
            risk_level="MEDIUM",
        )

        db_session.add(log)
        db_session.commit()

        assert log.id is not None
        assert log.action_required is True
        assert log.action_taken is True
        assert log.action_details is not None
        assert log.reviewed_at is not None
