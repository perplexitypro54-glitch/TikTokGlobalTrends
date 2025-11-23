"""
Report Generator

Generates reports from audit logs, collection logs, and compliance logs.
"""

import csv
import json
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from src.storage.models import (
    ActionType,
    AuditLog,
    CollectionLog,
    CollectionStatus,
    ComplianceLog,
)
from src.utils.logger import setup_logger

logger = setup_logger("report_generator")


class ReportType(str, Enum):
    """Types of reports that can be generated."""

    AUDIT = "AUDIT"
    COLLECTION = "COLLECTION"
    COMPLIANCE = "COMPLIANCE"
    SUMMARY = "SUMMARY"


class ReportFormat(str, Enum):
    """Output formats for reports."""

    JSON = "JSON"
    CSV = "CSV"
    HTML = "HTML"
    TEXT = "TEXT"


class ReportGenerator:
    """Generates various types of reports from log data."""

    def __init__(self, session: Session):
        self.session = session

    def generate_audit_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        action_type: Optional[ActionType] = None,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Generate audit report with optional filters."""
        logger.info(
            "Generating audit report",
            extra={
                "start_date": start_date,
                "end_date": end_date,
                "action_type": action_type,
                "user_id": user_id,
            },
        )

        query = self.session.query(AuditLog)

        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        if action_type:
            query = query.filter(AuditLog.action_type == action_type)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if status:
            query = query.filter(AuditLog.status == status)

        query = query.order_by(AuditLog.created_at.desc())
        results = query.all()

        report_data = []
        for log in results:
            report_data.append(
                {
                    "id": log.id,
                    "timestamp": log.created_at.isoformat(),
                    "action_type": log.action_type,
                    "user_id": log.user_id,
                    "username": log.username,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "description": log.description,
                    "status": log.status,
                    "ip_address": log.ip_address,
                    "execution_time_ms": log.execution_time_ms,
                    "error_message": log.error_message,
                }
            )

        logger.info(f"Audit report generated with {len(report_data)} records")
        return report_data

    def generate_collection_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        country_code: Optional[str] = None,
        status: Optional[CollectionStatus] = None,
    ) -> List[Dict[str, Any]]:
        """Generate collection report with optional filters."""
        logger.info(
            "Generating collection report",
            extra={
                "start_date": start_date,
                "end_date": end_date,
                "country_code": country_code,
                "status": status,
            },
        )

        query = self.session.query(CollectionLog)

        if start_date:
            query = query.filter(CollectionLog.started_at >= start_date)
        if end_date:
            query = query.filter(CollectionLog.started_at <= end_date)
        if country_code:
            query = query.filter(CollectionLog.country_code == country_code)
        if status:
            query = query.filter(CollectionLog.status == status)

        query = query.order_by(CollectionLog.started_at.desc())
        results = query.all()

        report_data = []
        for log in results:
            report_data.append(
                {
                    "id": log.id,
                    "started_at": log.started_at.isoformat(),
                    "completed_at": log.completed_at.isoformat() if log.completed_at else None,
                    "country_code": log.country_code,
                    "data_source": log.data_source,
                    "status": log.status,
                    "execution_time_seconds": log.execution_time_seconds,
                    "items_collected": log.items_collected,
                    "items_processed": log.items_processed,
                    "items_failed": log.items_failed,
                    "api_calls_made": log.api_calls_made,
                    "rate_limit_hit": log.rate_limit_hit,
                    "retry_count": log.retry_count,
                    "error_message": log.error_message,
                }
            )

        logger.info(f"Collection report generated with {len(report_data)} records")
        return report_data

    def generate_compliance_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        regulation: Optional[str] = None,
        risk_level: Optional[str] = None,
        action_required: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Generate compliance report with optional filters."""
        logger.info(
            "Generating compliance report",
            extra={
                "start_date": start_date,
                "end_date": end_date,
                "regulation": regulation,
                "risk_level": risk_level,
            },
        )

        query = self.session.query(ComplianceLog)

        if start_date:
            query = query.filter(ComplianceLog.created_at >= start_date)
        if end_date:
            query = query.filter(ComplianceLog.created_at <= end_date)
        if regulation:
            query = query.filter(ComplianceLog.regulation == regulation)
        if risk_level:
            query = query.filter(ComplianceLog.risk_level == risk_level)
        if action_required is not None:
            query = query.filter(ComplianceLog.action_required == action_required)

        query = query.order_by(ComplianceLog.created_at.desc())
        results = query.all()

        report_data = []
        for log in results:
            report_data.append(
                {
                    "id": log.id,
                    "timestamp": log.created_at.isoformat(),
                    "regulation": log.regulation,
                    "event_type": log.event_type,
                    "user_id": log.user_id,
                    "user_email": log.user_email,
                    "description": log.description,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "action_required": log.action_required,
                    "action_taken": log.action_taken,
                    "compliance_officer": log.compliance_officer,
                    "risk_level": log.risk_level,
                    "reviewed_at": log.reviewed_at.isoformat() if log.reviewed_at else None,
                }
            )

        logger.info(f"Compliance report generated with {len(report_data)} records")
        return report_data

    def generate_summary_report(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate summary report with statistics from all log types."""
        logger.info(
            "Generating summary report", extra={"start_date": start_date, "end_date": end_date}
        )

        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        audit_query = self.session.query(AuditLog).filter(
            and_(AuditLog.created_at >= start_date, AuditLog.created_at <= end_date)
        )

        collection_query = self.session.query(CollectionLog).filter(
            and_(CollectionLog.started_at >= start_date, CollectionLog.started_at <= end_date)
        )

        compliance_query = self.session.query(ComplianceLog).filter(
            and_(ComplianceLog.created_at >= start_date, ComplianceLog.created_at <= end_date)
        )

        audit_stats = {
            "total_actions": audit_query.count(),
            "successful_actions": audit_query.filter(AuditLog.status == "SUCCESS").count(),
            "failed_actions": audit_query.filter(AuditLog.status == "FAILED").count(),
            "actions_by_type": self._get_action_counts(audit_query),
        }

        collection_stats = {
            "total_collections": collection_query.count(),
            "successful_collections": collection_query.filter(
                CollectionLog.status == CollectionStatus.SUCCESS
            ).count(),
            "failed_collections": collection_query.filter(
                CollectionLog.status == CollectionStatus.FAILED
            ).count(),
            "total_items_collected": self.session.query(
                func.sum(CollectionLog.items_collected)
            )
            .filter(
                and_(
                    CollectionLog.started_at >= start_date, CollectionLog.started_at <= end_date
                )
            )
            .scalar()
            or 0,
            "rate_limit_incidents": collection_query.filter(
                CollectionLog.rate_limit_hit == True
            ).count(),
        }

        compliance_stats = {
            "total_events": compliance_query.count(),
            "high_risk_events": compliance_query.filter(
                ComplianceLog.risk_level == "HIGH"
            ).count(),
            "pending_actions": compliance_query.filter(
                and_(ComplianceLog.action_required == True, ComplianceLog.action_taken == False)
            ).count(),
            "events_by_regulation": self._get_compliance_counts(compliance_query),
        }

        summary = {
            "report_period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "audit_statistics": audit_stats,
            "collection_statistics": collection_stats,
            "compliance_statistics": compliance_stats,
            "generated_at": datetime.now().isoformat(),
        }

        logger.info("Summary report generated successfully")
        return summary

    def _get_action_counts(self, query) -> Dict[str, int]:
        """Get counts of actions by type."""
        results = (
            query.with_entities(AuditLog.action_type, func.count(AuditLog.id))
            .group_by(AuditLog.action_type)
            .all()
        )
        return {action_type: count for action_type, count in results}

    def _get_compliance_counts(self, query) -> Dict[str, int]:
        """Get counts of compliance events by regulation."""
        results = (
            query.with_entities(ComplianceLog.regulation, func.count(ComplianceLog.id))
            .group_by(ComplianceLog.regulation)
            .all()
        )
        return {regulation: count for regulation, count in results}

    def export_report(
        self, report_data: Any, format: ReportFormat, output_path: Path
    ) -> Path:
        """Export report data to specified format."""
        logger.info(
            f"Exporting report to {format}",
            extra={"output_path": str(output_path), "format": format},
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == ReportFormat.JSON:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

        elif format == ReportFormat.CSV:
            if isinstance(report_data, list) and report_data:
                with open(output_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=report_data[0].keys())
                    writer.writeheader()
                    writer.writerows(report_data)
            else:
                logger.warning("Cannot export non-list data to CSV format")
                raise ValueError("CSV format requires list data")

        elif format == ReportFormat.TEXT:
            with open(output_path, "w", encoding="utf-8") as f:
                if isinstance(report_data, dict):
                    for key, value in report_data.items():
                        f.write(f"{key}: {value}\n")
                elif isinstance(report_data, list):
                    for item in report_data:
                        f.write(f"{item}\n")
                else:
                    f.write(str(report_data))

        elif format == ReportFormat.HTML:
            html_content = self._generate_html_report(report_data)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

        logger.info(f"Report exported successfully to {output_path}")
        return output_path

    def _generate_html_report(self, report_data: Any) -> str:
        """Generate HTML formatted report."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>TikTok Global Trends - Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                table { border-collapse: collapse; width: 100%; margin-top: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #4CAF50; color: white; }
                tr:nth-child(even) { background-color: #f2f2f2; }
                .summary { background-color: #e7f3ff; padding: 15px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>TikTok Global Trends - Action Report</h1>
            <p>Generated at: {}</p>
        """.format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        if isinstance(report_data, dict):
            html += '<div class="summary">'
            html += "<h2>Summary</h2>"
            for key, value in report_data.items():
                html += f"<p><strong>{key}:</strong> {value}</p>"
            html += "</div>"

        elif isinstance(report_data, list) and report_data:
            html += "<table>"
            html += "<tr>"
            for key in report_data[0].keys():
                html += f"<th>{key}</th>"
            html += "</tr>"

            for item in report_data:
                html += "<tr>"
                for value in item.values():
                    html += f"<td>{value}</td>"
                html += "</tr>"
            html += "</table>"

        html += """
        </body>
        </html>
        """
        return html
