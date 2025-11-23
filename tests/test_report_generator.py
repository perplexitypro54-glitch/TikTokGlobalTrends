"""
Tests for ReportGenerator
"""

from datetime import datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.reporting import ReportFormat, ReportGenerator, ReportType
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


@pytest.fixture
def sample_audit_logs(db_session: Session):
    """Create sample audit logs."""
    logs = [
        AuditLog(
            action_type=ActionType.CREATE,
            user_id=1,
            username="user1",
            description="Created resource",
            status="SUCCESS",
            created_at=datetime.now() - timedelta(days=1),
        ),
        AuditLog(
            action_type=ActionType.UPDATE,
            user_id=1,
            username="user1",
            description="Updated resource",
            status="SUCCESS",
            created_at=datetime.now(),
        ),
        AuditLog(
            action_type=ActionType.DELETE,
            user_id=2,
            username="user2",
            description="Deleted resource",
            status="FAILED",
            error_message="Not authorized",
            created_at=datetime.now(),
        ),
    ]
    db_session.add_all(logs)
    db_session.commit()
    return logs


@pytest.fixture
def sample_collection_logs(db_session: Session):
    """Create sample collection logs."""
    logs = [
        CollectionLog(
            country_code=CountryCode.US,
            data_source=DataSourceType.OFFICIAL_API,
            status=CollectionStatus.SUCCESS,
            items_collected=100,
            items_processed=100,
            started_at=datetime.now() - timedelta(hours=2),
            completed_at=datetime.now() - timedelta(hours=1),
        ),
        CollectionLog(
            country_code=CountryCode.BR,
            data_source=DataSourceType.CREATIVE_CENTER,
            status=CollectionStatus.FAILED,
            items_collected=0,
            items_processed=0,
            error_message="Connection error",
            started_at=datetime.now() - timedelta(hours=1),
        ),
    ]
    db_session.add_all(logs)
    db_session.commit()
    return logs


@pytest.fixture
def sample_compliance_logs(db_session: Session):
    """Create sample compliance logs."""
    logs = [
        ComplianceLog(
            regulation=ComplianceRegulation.LGPD,
            event_type=ComplianceEventType.DATA_ACCESS,
            description="User accessed data",
            risk_level="LOW",
            created_at=datetime.now() - timedelta(days=1),
        ),
        ComplianceLog(
            regulation=ComplianceRegulation.GDPR,
            event_type=ComplianceEventType.DATA_BREACH,
            description="Security incident",
            risk_level="HIGH",
            action_required=True,
            created_at=datetime.now(),
        ),
    ]
    db_session.add_all(logs)
    db_session.commit()
    return logs


class TestReportGenerator:
    """Tests for ReportGenerator class."""

    def test_generate_audit_report(self, db_session: Session, sample_audit_logs):
        """Test generating audit report."""
        generator = ReportGenerator(db_session)
        report = generator.generate_audit_report()

        assert isinstance(report, list)
        assert len(report) == 3
        assert all("action_type" in item for item in report)
        assert all("username" in item for item in report)

    def test_generate_audit_report_filtered(self, db_session: Session, sample_audit_logs):
        """Test generating audit report with filters."""
        generator = ReportGenerator(db_session)
        report = generator.generate_audit_report(user_id=1)

        assert isinstance(report, list)
        assert len(report) == 2
        assert all(item["user_id"] == 1 for item in report)

    def test_generate_collection_report(self, db_session: Session, sample_collection_logs):
        """Test generating collection report."""
        generator = ReportGenerator(db_session)
        report = generator.generate_collection_report()

        assert isinstance(report, list)
        assert len(report) == 2
        assert all("country_code" in item for item in report)
        assert all("data_source" in item for item in report)

    def test_generate_collection_report_filtered(
        self, db_session: Session, sample_collection_logs
    ):
        """Test generating collection report with filters."""
        generator = ReportGenerator(db_session)
        report = generator.generate_collection_report(
            status=CollectionStatus.SUCCESS
        )

        assert isinstance(report, list)
        assert len(report) == 1
        assert report[0]["status"] == CollectionStatus.SUCCESS

    def test_generate_compliance_report(self, db_session: Session, sample_compliance_logs):
        """Test generating compliance report."""
        generator = ReportGenerator(db_session)
        report = generator.generate_compliance_report()

        assert isinstance(report, list)
        assert len(report) == 2
        assert all("regulation" in item for item in report)
        assert all("event_type" in item for item in report)

    def test_generate_compliance_report_filtered(
        self, db_session: Session, sample_compliance_logs
    ):
        """Test generating compliance report with filters."""
        generator = ReportGenerator(db_session)
        report = generator.generate_compliance_report(risk_level="HIGH")

        assert isinstance(report, list)
        assert len(report) == 1
        assert report[0]["risk_level"] == "HIGH"

    def test_generate_summary_report(
        self,
        db_session: Session,
        sample_audit_logs,
        sample_collection_logs,
        sample_compliance_logs,
    ):
        """Test generating summary report."""
        generator = ReportGenerator(db_session)
        report = generator.generate_summary_report()

        assert isinstance(report, dict)
        assert "report_period" in report
        assert "audit_statistics" in report
        assert "collection_statistics" in report
        assert "compliance_statistics" in report

        assert report["audit_statistics"]["total_actions"] == 3
        assert report["collection_statistics"]["total_collections"] == 2
        assert report["compliance_statistics"]["total_events"] == 2

    def test_export_report_json(self, db_session: Session, sample_audit_logs, tmp_path):
        """Test exporting report to JSON."""
        generator = ReportGenerator(db_session)
        report = generator.generate_audit_report()

        output_path = tmp_path / "report.json"
        result_path = generator.export_report(report, ReportFormat.JSON, output_path)

        assert result_path.exists()
        assert result_path.read_text()

    def test_export_report_csv(self, db_session: Session, sample_audit_logs, tmp_path):
        """Test exporting report to CSV."""
        generator = ReportGenerator(db_session)
        report = generator.generate_audit_report()

        output_path = tmp_path / "report.csv"
        result_path = generator.export_report(report, ReportFormat.CSV, output_path)

        assert result_path.exists()
        content = result_path.read_text()
        assert "action_type" in content
        assert "username" in content

    def test_export_report_html(self, db_session: Session, sample_audit_logs, tmp_path):
        """Test exporting report to HTML."""
        generator = ReportGenerator(db_session)
        report = generator.generate_audit_report()

        output_path = tmp_path / "report.html"
        result_path = generator.export_report(report, ReportFormat.HTML, output_path)

        assert result_path.exists()
        content = result_path.read_text()
        assert "<html>" in content
        assert "<table>" in content

    def test_export_report_text(self, db_session: Session, sample_audit_logs, tmp_path):
        """Test exporting report to TEXT."""
        generator = ReportGenerator(db_session)
        report = generator.generate_audit_report()

        output_path = tmp_path / "report.txt"
        result_path = generator.export_report(report, ReportFormat.TEXT, output_path)

        assert result_path.exists()
        assert result_path.read_text()
