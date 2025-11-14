#!/usr/bin/env python3
"""
Example: Using the Reporting System

This example demonstrates how to create logs and generate reports.
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.reporting import ReportFormat, ReportGenerator
from src.storage.database import DatabaseManager
from src.storage.models import (
    ActionType,
    AuditLog,
    CollectionLog,
    CollectionStatus,
    ComplianceEventType,
    ComplianceLog,
    ComplianceRegulation,
)
from src.storage.models.enums import CountryCode, DataSourceType


def create_sample_logs(db_manager: DatabaseManager):
    """Create sample logs for demonstration."""
    print("📝 Creating sample logs...")

    with db_manager.get_session() as session:
        audit_log = AuditLog(
            action_type=ActionType.CREATE,
            user_id=1,
            username="admin",
            resource_type="Video",
            resource_id="12345",
            description="Created new trending video record",
            status="SUCCESS",
            ip_address="192.168.1.1",
            execution_time_ms=120,
        )
        session.add(audit_log)

        collection_log = CollectionLog(
            country_code=CountryCode.BR,
            data_source=DataSourceType.OFFICIAL_API,
            status=CollectionStatus.SUCCESS,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            items_collected=150,
            items_processed=150,
            items_failed=0,
            api_calls_made=5,
            execution_time_seconds=12.5,
        )
        session.add(collection_log)

        compliance_log = ComplianceLog(
            regulation=ComplianceRegulation.LGPD,
            event_type=ComplianceEventType.DATA_ACCESS,
            user_id=10,
            user_email="user@example.com",
            description="User requested access to personal data",
            risk_level="LOW",
            action_required=False,
            action_taken=True,
        )
        session.add(compliance_log)

        session.commit()
        print("✅ Sample logs created successfully!")


def generate_reports(db_manager: DatabaseManager):
    """Generate various reports."""
    print("\n📊 Generating reports...\n")

    with db_manager.get_session() as session:
        generator = ReportGenerator(session)

        print("1️⃣ Audit Report:")
        audit_report = generator.generate_audit_report()
        print(f"   Found {len(audit_report)} audit log entries")
        if audit_report:
            latest = audit_report[0]
            print(f"   Latest: {latest['action_type']} by {latest.get('username', 'N/A')}")

        print("\n2️⃣ Collection Report:")
        collection_report = generator.generate_collection_report()
        print(f"   Found {len(collection_report)} collection log entries")
        if collection_report:
            latest = collection_report[0]
            print(
                f"   Latest: {latest['country_code']} from {latest['data_source']} - "
                f"{latest['status']}"
            )

        print("\n3️⃣ Compliance Report:")
        compliance_report = generator.generate_compliance_report()
        print(f"   Found {len(compliance_report)} compliance log entries")
        if compliance_report:
            latest = compliance_report[0]
            print(
                f"   Latest: {latest['regulation']} - {latest['event_type']} - "
                f"Risk: {latest['risk_level']}"
            )

        print("\n4️⃣ Summary Report:")
        summary = generator.generate_summary_report()
        print(f"   Period: {summary['report_period']['start'][:10]} to "
              f"{summary['report_period']['end'][:10]}")
        print(f"   Total Actions: {summary['audit_statistics']['total_actions']}")
        print(f"   Total Collections: {summary['collection_statistics']['total_collections']}")
        print(f"   Total Compliance Events: {summary['compliance_statistics']['total_events']}")

        print("\n📁 Exporting reports...")
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)

        generator.export_report(
            audit_report, ReportFormat.JSON, reports_dir / "audit_example.json"
        )
        print("   ✓ audit_example.json")

        generator.export_report(
            collection_report, ReportFormat.JSON, reports_dir / "collection_example.json"
        )
        print("   ✓ collection_example.json")

        generator.export_report(
            compliance_report, ReportFormat.JSON, reports_dir / "compliance_example.json"
        )
        print("   ✓ compliance_example.json")

        generator.export_report(summary, ReportFormat.JSON, reports_dir / "summary_example.json")
        print("   ✓ summary_example.json")

        generator.export_report(summary, ReportFormat.HTML, reports_dir / "summary_example.html")
        print("   ✓ summary_example.html")


def main():
    """Main function."""
    print("🚀 TikTok Global Trends - Reporting System Example\n")

    db_manager = DatabaseManager("sqlite:///./data/tiktok_trends.db")
    print(f"📂 Database: sqlite:///./data/tiktok_trends.db\n")

    create_sample_logs(db_manager)
    generate_reports(db_manager)

    print("\n✅ Example completed successfully!")
    print("\n📖 Check the 'reports/' directory for generated reports")
    print("📚 See docs/RELATORIO_ACOES.md for full documentation")


if __name__ == "__main__":
    main()
