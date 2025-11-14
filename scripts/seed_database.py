#!/usr/bin/env python3
"""
Seed Database Script

Populates the database with initial data using Alembic migrations.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import DatabaseManager
from src.storage.models import Country
from src.storage.models.enums import CountryCode
from src.utils.logger import setup_logger


def seed_initial_data():
    """Seed the database with initial data."""
    logger = setup_logger("database_seed")

    # Initialize database manager
    db = DatabaseManager("sqlite:///./data/tiktok_trends.db")

    with db.get_session() as session:
        # Check if countries already exist
        existing_countries = session.query(Country).count()
        if existing_countries > 0:
            logger.info(f"Database already has {existing_countries} countries. Skipping seed.")
            return

        logger.info("Seeding initial data...")

        # Add initial countries
        countries_data = [
            {
                "code": CountryCode.US,
                "name": "United States",
                "users_in_millions": 150.0,
                "growth_rate": 12.0,
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
                "users_in_millions": 68.5,
                "growth_rate": 15.0,
                "timezone": "America/Mexico_City",
            },
            {
                "code": CountryCode.JP,
                "name": "Japan",
                "users_in_millions": 23.5,
                "growth_rate": 8.0,
                "timezone": "Asia/Tokyo",
            },
        ]

        for country_data in countries_data:
            country = Country(**country_data)
            session.add(country)
            logger.info(f"Added country: {country.name}")

        session.commit()
        logger.info("Database seeding complete!")


if __name__ == "__main__":
    seed_initial_data()
