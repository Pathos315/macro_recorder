import json
from pathlib import Path
from typing import Any, Dict, List

from src.config import logger
from src.models import MacroEvent


class MacroStorage:
    """Handles saving and loading macro events."""

    @staticmethod
    def save_to_file(events: List[MacroEvent], filename: str) -> None:
        """
        Save macro events to a file.

        Args:
            events: List of macro events
            filename: Path to save the file
        """
        # Create directory if it doesn't exist
        file_path = Path(filename)

        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert events to dictionaries with relative timing
        serializable_events = []

        if events:
            prev_timestamp = events[0].timestamp

            for event in events:
                event_dict = event.to_dict()

                # Add time_diff for replay timing
                time_diff = event.timestamp - prev_timestamp
                event_dict["time_diff"] = time_diff

                serializable_events.append(event_dict)
                prev_timestamp = event.timestamp

        # Save to file
        try:
            with file_path.open("w") as file:
                json.dump(serializable_events, file, indent=2)
            logger.info(f"Saved {len(serializable_events)} events to {filename}")
        except (IOError, OSError) as e:
            logger.error(f"Error saving to file {filename}: {e}")
            raise

    @staticmethod
    def load_from_file(filename: str) -> List[Dict[str, Any]]:
        """
        Load macro events from a file.

        Args:
            filename: Path to the file

        Returns:
            List of event dictionaries
        """
        file_path = Path(filename)

        try:
            with file_path.open("r") as file:
                events = json.load(file)
            logger.info(f"Loaded {len(events)} events from {filename}")
            return events
        except FileNotFoundError:
            logger.error(f"File not found: {filename}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in file: {filename}")
            raise
