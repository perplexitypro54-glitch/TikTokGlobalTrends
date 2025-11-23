"""
Compliance Log Model

Tracks compliance-related events for LGPD, GDPR, CCPA, and PDPA regulations.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.storage.models.base import Base, TimestampMixin


class ComplianceRegulation(str, Enum):
    """Supported compliance regulations."""

    LGPD = "LGPD"
    GDPR = "GDPR"
    CCPA = "CCPA"
    PDPA = "PDPA"


class ComplianceEventType(str, Enum):
    """Types of compliance events."""

    DATA_ACCESS = "DATA_ACCESS"
    DATA_EXPORT = "DATA_EXPORT"
    DATA_DELETE = "DATA_DELETE"
    DATA_RETENTION = "DATA_RETENTION"
    CONSENT_GIVEN = "CONSENT_GIVEN"
    CONSENT_REVOKED = "CONSENT_REVOKED"
    DATA_BREACH = "DATA_BREACH"
    PRIVACY_REQUEST = "PRIVACY_REQUEST"
    DATA_ANONYMIZATION = "DATA_ANONYMIZATION"
    AUDIT_TRAIL = "AUDIT_TRAIL"
    POLICY_UPDATE = "POLICY_UPDATE"
    USER_RIGHT_REQUEST = "USER_RIGHT_REQUEST"


class ComplianceLog(Base, TimestampMixin):
    """Compliance log model for tracking regulatory compliance events."""

    __tablename__ = "compliance_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    regulation: Mapped[ComplianceRegulation] = mapped_column(String(20), nullable=False, index=True)
    event_type: Mapped[ComplianceEventType] = mapped_column(String(50), nullable=False, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    user_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    action_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    action_taken: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    action_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    compliance_officer: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    risk_level: Mapped[str] = mapped_column(
        String(20), default="LOW", nullable=False, index=True
    )
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("idx_compliance_regulation", "regulation"),
        Index("idx_compliance_event_type", "event_type"),
        Index("idx_compliance_user_id", "user_id"),
        Index("idx_compliance_created_at", "created_at"),
        Index("idx_compliance_risk_level", "risk_level"),
        Index("idx_compliance_action_required", "action_required"),
    )

    def __repr__(self) -> str:
        return (
            f"<ComplianceLog(id={self.id}, regulation={self.regulation}, "
            f"event={self.event_type}, risk={self.risk_level})>"
        )
