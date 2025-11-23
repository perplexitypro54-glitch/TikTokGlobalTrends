#!/usr/bin/env python3
"""
Generate Reports Script

CLI tool to generate various reports from audit, collection, and compliance logs.

Usage:
    python scripts/generate_report.py --type audit --format json --output reports/audit.json
    python scripts/generate_report.py --type collection --days 7 --format csv
    python scripts/generate_report.py --type summary --format html
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

from src.reporting import ReportFormat, ReportGenerator, ReportType
from src.storage.database import DatabaseManager
from src.storage.models import ActionType, CollectionStatus
from src.utils.logger import setup_logger

logger = setup_logger("generate_report")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate reports from TikTok Global Trends logs"
    )

    parser.add_argument(
        "--type",
        type=str,
        choices=["audit", "collection", "compliance", "summary"],
        required=True,
        help="Type of report to generate",
    )

    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "csv", "html", "text"],
        default="json",
        help="Output format (default: json)",
    )

    parser.add_argument(
        "--output", type=str, help="Output file path (default: reports/<type>_<timestamp>.<ext>)"
    )

    parser.add_argument("--days", type=int, help="Number of days to include (default: 30)")

    parser.add_argument("--start-date", type=str, help="Start date (YYYY-MM-DD)")

    parser.add_argument("--end-date", type=str, help="End date (YYYY-MM-DD)")

    parser.add_argument(
        "--action-type", type=str, help="Filter by action type (audit report only)"
    )

    parser.add_argument("--user-id", type=int, help="Filter by user ID (audit report only)")

    parser.add_argument("--country", type=str, help="Filter by country code (collection only)")

    parser.add_argument("--status", type=str, help="Filter by status")

    parser.add_argument("--regulation", type=str, help="Filter by regulation (compliance only)")

    parser.add_argument(
        "--risk-level", type=str, help="Filter by risk level (compliance only)"
    )

    parser.add_argument(
        "--database-url",
        type=str,
        default="sqlite:///./data/tiktok_trends.db",
        help="Database URL",
    )

    return parser.parse_args()


def get_date_range(args):
    """Calculate date range from arguments."""
    if args.start_date:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    elif args.days:
        start_date = datetime.now() - timedelta(days=args.days)
    else:
        start_date = datetime.now() - timedelta(days=30)

    if args.end_date:
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
    else:
        end_date = datetime.now()

    return start_date, end_date


def get_output_path(args, report_type: str) -> Path:
    """Generate output file path."""
    if args.output:
        return Path(args.output)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    format_ext = args.format.lower()
    filename = f"{report_type}_{timestamp}.{format_ext}"

    output_dir = Path("reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    return output_dir / filename


def generate_audit_report(generator: ReportGenerator, args) -> list:
    """Generate audit report."""
    start_date, end_date = get_date_range(args)

    action_type = None
    if args.action_type:
        try:
            action_type = ActionType[args.action_type.upper()]
        except KeyError:
            logger.error(f"Invalid action type: {args.action_type}")
            sys.exit(1)

    return generator.generate_audit_report(
        start_date=start_date,
        end_date=end_date,
        action_type=action_type,
        user_id=args.user_id,
        status=args.status,
    )


def generate_collection_report(generator: ReportGenerator, args) -> list:
    """Generate collection report."""
    start_date, end_date = get_date_range(args)

    status = None
    if args.status:
        try:
            status = CollectionStatus[args.status.upper()]
        except KeyError:
            logger.error(f"Invalid status: {args.status}")
            sys.exit(1)

    return generator.generate_collection_report(
        start_date=start_date, end_date=end_date, country_code=args.country, status=status
    )


def generate_compliance_report(generator: ReportGenerator, args) -> list:
    """Generate compliance report."""
    start_date, end_date = get_date_range(args)

    return generator.generate_compliance_report(
        start_date=start_date,
        end_date=end_date,
        regulation=args.regulation,
        risk_level=args.risk_level,
    )


def generate_summary_report(generator: ReportGenerator, args) -> dict:
    """Generate summary report."""
    start_date, end_date = get_date_range(args)
    return generator.generate_summary_report(start_date=start_date, end_date=end_date)


def main():
    """Main function."""
    args = parse_args()

    logger.info(
        f"Starting report generation: type={args.type}, format={args.format}",
        extra={"report_type": args.type, "format": args.format},
    )

    try:
        db_manager = DatabaseManager(args.database_url)
        logger.info(f"Connected to database: {args.database_url}")

        with db_manager.get_session() as session:
            generator = ReportGenerator(session)

            if args.type == "audit":
                report_data = generate_audit_report(generator, args)
            elif args.type == "collection":
                report_data = generate_collection_report(generator, args)
            elif args.type == "compliance":
                report_data = generate_compliance_report(generator, args)
            elif args.type == "summary":
                report_data = generate_summary_report(generator, args)
            else:
                logger.error(f"Unknown report type: {args.type}")
                sys.exit(1)

            output_path = get_output_path(args, args.type)

            format_enum = ReportFormat[args.format.upper()]
            generator.export_report(report_data, format_enum, output_path)

            print(f"\n✅ Report generated successfully!")
            print(f"📄 Output: {output_path}")
            print(f"📊 Format: {args.format.upper()}")

            if isinstance(report_data, list):
                print(f"📈 Records: {len(report_data)}")
            elif isinstance(report_data, dict) and "report_period" in report_data:
                print(f"📅 Period: {report_data['report_period']['start']} to {report_data['report_period']['end']}")

            logger.info("Report generation completed successfully")

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
