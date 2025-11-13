"""
TikTok Global Trends - Main Entry Point

This module serves as the primary orchestrator for the TikTok Global Trends application.
It initializes all necessary components and launches the UI or backend services.
"""

import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger


def initialize_application() -> None:
    """
    Initialize the TikTok Global Trends application.

    Sets up logging, configuration, and prepares all components for startup.
    """
    # Setup logging
    logger = setup_logger("tiktok_global_trends")
    logger.info("TikTok Global Trends initialized")

    # Log startup information
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Application root: {Path(__file__).parent}")


def main() -> int:
    """
    Main entry point for the TikTok Global Trends application.

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        initialize_application()
        logger = logging.getLogger("tiktok_global_trends")
        logger.info("TikTok Global Trends initialized")

        # TODO: Implement UI launcher (PySimpleGUI)
        # from src.ui.main_window import launch_ui
        # launch_ui()

        # TODO: Implement API server initialization
        # from src.api.server import run_server
        # run_server()

        return 0
    except Exception as e:
        logger = logging.getLogger("tiktok_global_trends")
        logger.exception("Fatal error during initialization: %s", str(e))
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
