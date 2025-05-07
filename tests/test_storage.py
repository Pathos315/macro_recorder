import pytest
import json
from unittest.mock import patch, MagicMock
from src.storage import MacroStorage
from src.models import (
    MouseMoveEvent,
    MouseButtonEvent,
    Position,
    MouseButton,
)


class TestMacroStorage:
    @patch("json.dump")
    @patch("src.storage.Path")  # Patch Path where it's used, not where it's defined
    def test_save_to_file(self, mock_path_class, mock_json_dump):
        """Test saving macro events to a file."""
        # Create test events
        event1 = MouseMoveEvent(timestamp=1000.0, position=Position(100, 200))
        event2 = MouseButtonEvent(
            timestamp=1001.0,
            position=Position(100, 200),
            button=MouseButton.LEFT,
            pressed=True,
        )

        events = [event1, event2]
        filename = "macros/test_macro.json"

        # Set up mocks
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.parent = MagicMock()

        # Mock the file opening operation
        mock_file = MagicMock()
        mock_path_instance.open.return_value.__enter__.return_value = mock_file

        # Call the method
        MacroStorage.save_to_file(events, filename)

        # Check that Path was created with the correct filename
        mock_path_class.assert_called_once_with(filename)

        # Check that directory was created
        mock_path_instance.parent.mkdir.assert_called_once_with(
            parents=True, exist_ok=True
        )

        # Check that file was opened in write mode
        mock_path_instance.open.assert_called_once_with("w")

        # Verify json.dump was called with the expected data
        mock_json_dump.assert_called_once()

        # Extract the data that was passed to json.dump
        serializable_events = mock_json_dump.call_args[0][0]

        assert len(serializable_events) == 2

        # Check first event - NOTE: position is returned as a tuple, not a list
        assert serializable_events[0]["action"] == "move"
        assert serializable_events[0]["timestamp"] == 1000.0
        assert serializable_events[0]["position"] == (100, 200)  # Tuple, not list
        assert serializable_events[0]["time_diff"] == 0.0

        # Check second event
        assert serializable_events[1]["action"] == "press"
        assert serializable_events[1]["timestamp"] == 1001.0
        assert serializable_events[1]["position"] == (100, 200)  # Tuple, not list
        assert serializable_events[1]["button"] == "Button.left"
        assert (
            serializable_events[1]["time_diff"] == 1.0
        )  # time diff from previous event

    @patch("src.storage.Path")  # Patch Path where it's used
    def test_load_from_file(self, mock_path_class):
        """Test loading macro events from a file."""
        # Sample events data as JSON string - note positions as arrays since JSON doesn't support tuples
        sample_json = json.dumps(
            [
                {
                    "action": "move",
                    "timestamp": 1000.0,
                    "position": [100, 200],  # JSON uses arrays (lists), not tuples
                    "time_diff": 0.0,
                },
                {
                    "action": "press",
                    "timestamp": 1001.0,
                    "position": [100, 200],  # JSON uses arrays (lists), not tuples
                    "button": "Button.left",
                    "time_diff": 1.0,
                },
            ]
        )

        # Set up mock path instance
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance

        # Mock the file object to return our sample JSON when read
        mock_file = MagicMock()
        mock_file.read.return_value = sample_json

        # Mock the open context manager to return our file
        mock_path_instance.open.return_value.__enter__.return_value = mock_file

        # Call the method
        events = MacroStorage.load_from_file("macros/test_macro.json")

        # Check that Path was created with the correct filename
        mock_path_class.assert_called_once_with("macros/test_macro.json")

        # Check that file was opened in read mode
        mock_path_instance.open.assert_called_once_with("r")

        # Verify results from the parse - note positions remain as lists when loaded from JSON
        assert len(events) == 2

        assert events[0]["action"] == "move"
        assert events[0]["timestamp"] == 1000.0
        assert events[0]["position"] == [100, 200]  # From JSON, remains a list
        assert events[0]["time_diff"] == 0.0

        assert events[1]["action"] == "press"
        assert events[1]["timestamp"] == 1001.0
        assert events[1]["position"] == [100, 200]  # From JSON, remains a list
        assert events[1]["button"] == "Button.left"
        assert events[1]["time_diff"] == 1.0

    @patch("src.storage.Path")  # Patch Path where it's used
    def test_load_from_file_file_not_found(self, mock_path_class):
        """Test handling of FileNotFoundError."""
        # Set up mock Path instance
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance

        # Make the open method raise FileNotFoundError
        mock_path_instance.open.side_effect = FileNotFoundError()

        # Call the method and verify it raises FileNotFoundError
        with pytest.raises(FileNotFoundError):
            MacroStorage.load_from_file("nonexistent_file.json")

        # Verify Path was created with the correct filename
        mock_path_class.assert_called_once_with("nonexistent_file.json")

    @patch("src.storage.Path")  # Patch Path where it's used
    def test_load_from_file_invalid_json(self, mock_path_class):
        """Test handling of invalid JSON."""
        # Set up invalid JSON string
        invalid_json = "{ this is not valid JSON }"

        # Set up mock Path instance
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance

        # Mock the file object to return invalid JSON when read
        mock_file = MagicMock()
        mock_file.read.return_value = invalid_json

        # Mock the open context manager to return our file
        mock_path_instance.open.return_value.__enter__.return_value = mock_file

        # Call the method and verify it raises JSONDecodeError
        with pytest.raises(json.JSONDecodeError):
            MacroStorage.load_from_file("invalid_json.json")

        # Verify Path was created with the correct filename
        mock_path_class.assert_called_once_with("invalid_json.json")
