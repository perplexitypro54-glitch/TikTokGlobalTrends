"""
Initialize Database

Script to create database tables and seed initial data.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import DatabaseManager
from src.storage.models import Country
from src.storage.models.enums import CountryCode
from src.utils.logger import setup_logger

logger = setup_logger("database_init")


def init_database(database_url: str = "sqlite:///./data/tiktok_trends.db"):
    """
    Initialize database with tables and seed data.

    Args:
        database_url: Database connection URL
    """
    logger.info(f"Initializing database: {database_url}")

    # Create database manager
    db_manager = DatabaseManager(database_url)

    # Create all tables
    logger.info("Creating database tables...")
    db_manager.create_tables()
    logger.info("Database tables created successfully")

    # Seed initial countries
    logger.info("Seeding initial data...")
    session = db_manager.get_session()

    countries_data = [
        {
            "code": CountryCode.US,
            "name": "United States",
            "users_in_millions": 136.0,
            "growth_rate": 5.0,
            "timezone": "America/New_York",
        },
        {
            "code": CountryCode.BR,
            "name": "Brazil",
            "users_in_millions": 91.7,
            "growth_rate": 18.0,
            "timezone": "America/Sao_Paulo",
        },
        {
            "code": CountryCode.ID,
            "name": "Indonesia",
            "users_in_millions": 107.7,
            "growth_rate": 22.0,
            "timezone": "Asia/Jakarta",
        },
        {
            "code": CountryCode.MX,
            "name": "Mexico",
            "users_in_millions": 85.4,
            "growth_rate": 16.0,
            "timezone": "America/Mexico_City",
        },
        {
            "code": CountryCode.JP,
            "name": "Japan",
            "users_in_millions": 38.0,
            "growth_rate": 2.0,
            "timezone": "Asia/Tokyo",
        },
    ]

    for country_data in countries_data:
        # Check if country already exists
        existing = (
            session.query(Country).filter(Country.code == country_data["code"]).first()
        )
        if not existing:
            country = Country(**country_data)
            session.add(country)
            logger.info(f"Added country: {country_data['name']}")

    session.commit()
    session.close()

    logger.info("Database initialization complete!")
    logger.info(f"Database location: {database_url}")


if __name__ == "__main__":
    import os

    # Create data directory if it doesn't exist
    os.makedirs("./data", exist_ok=True)

    # Initialize database
    init_database()
