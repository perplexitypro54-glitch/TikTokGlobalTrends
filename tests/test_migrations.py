"""Integration tests for Alembic migrations."""
from __future__ import annotations

from pathlib import Path

import sqlalchemy as sa
from alembic import command
from alembic.config import Config


def _get_alembic_config(database_path: Path) -> Config:
    """Create an Alembic config instance pointing to a temporary database."""
    project_root = Path(__file__).resolve().parents[1]
    alembic_ini_path = project_root / "alembic.ini"
    alembic_config = Config(str(alembic_ini_path))

    # Ensure Alembic uses absolute paths so the test can run from any location.
    alembic_config.set_main_option("script_location", str(project_root / "alembic"))
    alembic_config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path.as_posix()}")

    return alembic_config


def test_migrations_upgrade_and_downgrade(tmp_path):
    """Validate that Alembic migrations upgrade and downgrade successfully."""
    database_file = tmp_path / "test_migrations.db"
    config = _get_alembic_config(database_file)

    # Apply all migrations.
    command.upgrade(config, "head")

    engine = sa.create_engine(f"sqlite:///{database_file.as_posix()}")
    inspector = sa.inspect(engine)
    tables_after_upgrade = set(inspector.get_table_names())

    expected_tables = {
        "alembic_version",
        "countries",
        "creators",
        "hashtags",
        "sounds",
        "trends",
        "videos",
        "video_hashtags",
        "sound_videos",
        "trend_hashtags",
        "trend_sounds",
        "trend_creators",
    }
    assert expected_tables.issubset(tables_after_upgrade)

    # Roll back to base and ensure the schema is removed.
    command.downgrade(config, "base")
    engine.dispose()
    engine = sa.create_engine(f"sqlite:///{database_file.as_posix()}")
    inspector = sa.inspect(engine)
    tables_after_downgrade = set(inspector.get_table_names())

    for table_name in expected_tables - {"alembic_version"}:
        assert table_name not in tables_after_downgrade

    engine.dispose()
