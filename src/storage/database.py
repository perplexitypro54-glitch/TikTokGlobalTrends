"""
Database Module

Manages all database operations including CRUD operations and schema management.
"""

from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.storage.models import Base, Country, Creator, Hashtag, Video


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self, database_url: str):
        """
        Initialize database manager.

        Args:
            database_url: SQLAlchemy database URL
        """
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_session(self) -> Session:
        """
        Get database session.

        Returns:
            SQLAlchemy session
        """
        return self.SessionLocal()

    def create_tables(self) -> None:
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self) -> None:
        """Drop all tables from the database."""
        Base.metadata.drop_all(bind=self.engine)

    def save_hashtag(self, hashtag_data: dict) -> dict:
        """
        Save hashtag to database.

        Args:
            hashtag_data: Hashtag information dictionary

        Returns:
            Saved hashtag data
        """
        with self.get_session() as session:
            hashtag = Hashtag(**hashtag_data)
            session.add(hashtag)
            session.commit()
            session.refresh(hashtag)
            return {
                "id": hashtag.id,
                "name": hashtag.name,
                "rank": hashtag.rank,
                "country_id": hashtag.country_id,
            }

    def save_video(self, video_data: dict) -> dict:
        """
        Save video to database.

        Args:
            video_data: Video information dictionary

        Returns:
            Saved video data
        """
        with self.get_session() as session:
            video = Video(**video_data)
            session.add(video)
            session.commit()
            session.refresh(video)
            return {
                "id": video.id,
                "tiktok_video_id": video.tiktok_video_id,
                "creator_id": video.creator_id,
            }

    def save_creator(self, creator_data: dict) -> dict:
        """
        Save creator to database.

        Args:
            creator_data: Creator information dictionary

        Returns:
            Saved creator data
        """
        with self.get_session() as session:
            creator = Creator(**creator_data)
            session.add(creator)
            session.commit()
            session.refresh(creator)
            return {
                "id": creator.id,
                "username": creator.username,
                "tiktok_creator_id": creator.tiktok_creator_id,
            }

    def get_country_by_code(self, country_code: str) -> Optional[Country]:
        """
        Get country by country code.

        Args:
            country_code: Two-letter country code

        Returns:
            Country instance or None
        """
        with self.get_session() as session:
            return session.query(Country).filter(Country.code == country_code).first()
