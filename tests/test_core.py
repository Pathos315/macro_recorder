import json
import threading
import time
from unittest.mock import ANY, MagicMock, patch

from src.config import Configuration
from src.core import MacroPlayer, MacroRecorder
from src.models import (
    KeyboardEvent,
    MouseButton,
    MouseButtonEvent,
    MouseMoveEvent,
    Position,
)


class TestMacroRecorder:
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Configuration()
        # Mocking screen dimensions to avoid actual screen queries
        self.config.screen_width = 1920
        self.config.screen_height = 1080
        self.config.min_move_distance = 5
        self.config.min_move_time = 0.02

        # Patch dependencies
        self.ui_patcher = patch("src.core.CountdownUI")
        self.mouse_adapter_patcher = patch("src.core.MouseInputAdapter")
        self.keyboard_adapter_patcher = patch("src.core.KeyboardInputAdapter")

        self.mock_ui = self.ui_patcher.start()
        self.mock_mouse_adapter = self.mouse_adapter_patcher.start()
        self.mock_keyboard_adapter = self.keyboard_adapter_patcher.start()

        # Setup mock instances
        self.mock_ui_instance = MagicMock()
        self.mock_mouse_adapter_instance = MagicMock()
        self.mock_keyboard_adapter_instance = MagicMock()

        self.mock_ui.return_value = self.mock_ui_instance
        self.mock_mouse_adapter.return_value = self.mock_mouse_adapter_instance
        self.mock_keyboard_adapter.return_value = self.mock_keyboard_adapter_instance

        # Create recorder
        self.recorder = MacroRecorder(self.config)

    def teardown_method(self):
        """Tear down test fixtures."""
        self.ui_patcher.stop()
        self.mouse_adapter_patcher.stop()
        self.keyboard_adapter_patcher.stop()

    def test_init(self):
        """Test initialization of MacroRecorder."""
        assert self.recorder.config == self.config
        assert hasattr(self.recorder, "events")
        assert isinstance(self.recorder.events, list)
        assert len(self.recorder.events) == 0
        assert hasattr(self.recorder, "lock")
        assert isinstance(self.recorder.lock, threading.Lock)
        assert self.recorder.last_recorded_pos is None
        assert self.recorder.last_move_time == 0.0

    def test_start_recording(self):
        """Test start_recording method."""
        # Call the method
        self.recorder.start_recording()

        # Verify UI countdown
        self.mock_ui_instance.show_countdown.assert_called_once_with("record")

        # Verify adapters started
        self.mock_mouse_adapter_instance.start_listening.assert_called_once()
        self.mock_keyboard_adapter_instance.start_listening.assert_called_once()

        # Verify state reset
        assert self.recorder.events == []
        assert self.recorder.last_recorded_pos is None
        assert self.recorder.last_move_time == 0.0

    def test_stop_recording(self):
        """Test stop_recording method."""
        # Call the method
        self.recorder.stop_recording()

        # Verify adapters stopped
        self.mock_mouse_adapter_instance.stop_listening.assert_called_once()
        self.mock_keyboard_adapter_instance.stop_listening.assert_called_once()

    @patch("src.core.MacroStorage")
    def test_save_recording(self, mock_storage):
        """Test save_recording method."""
        # Setup
        self.recorder.events = [MagicMock(), MagicMock()]

        # Call the method
        self.recorder.save_recording("macros/test.json")

        # Verify storage was used
        mock_storage.save_to_file.assert_called_once_with(
            self.recorder.events, "macros/test.json"
        )

    @patch("src.core.MacroStorage")
    def test_save_recording_empty(self, mock_storage):
        """Test save_recording method with no events."""
        # Call the method with empty events
        self.recorder.events = []
        self.recorder.save_recording("macros/test.json")

        # Verify storage was not used
        mock_storage.save_to_file.assert_not_called()

    def test_on_mouse_move_first_move(self):
        """Test _on_mouse_move for the first movement."""
        current_time = time.time()

        # Mock time.time() to return a fixed value
        with patch("time.time", return_value=current_time):
            # Call the method for the first time
            self.recorder._on_mouse_move(Position(100, 200))

            # Check that last_recorded_pos was set but no event was added
            assert self.recorder.last_recorded_pos.x == 100
            assert self.recorder.last_recorded_pos.y == 200
            assert self.recorder.last_move_time == current_time
            assert len(self.recorder.events) == 0

    def test_on_mouse_move_below_threshold(self):
        """Test _on_mouse_move with movement below threshold."""
        # Setup initial state
        current_time = time.time()
        self.recorder.last_recorded_pos = Position(100, 200)
        self.recorder.last_move_time = current_time - 0.01  # Below min_move_time

        # Mock time.time() to return a fixed value
        with patch("time.time", return_value=current_time):
            # Move by 3 pixels (below min_move_distance of 5)
            self.recorder._on_mouse_move(Position(102, 201))

            # Check that no event was added
            assert len(self.recorder.events) == 0
            # Last position should not change
            assert self.recorder.last_recorded_pos.x == 100
            assert self.recorder.last_recorded_pos.y == 200

    def test_on_mouse_move_above_distance_threshold(self):
        """Test _on_mouse_move with movement above distance threshold."""
        # Setup initial state
        current_time = time.time()
        self.recorder.last_recorded_pos = Position(100, 200)
        self.recorder.last_move_time = current_time - 0.01  # Below min_move_time

        # Mock time.time() to return a fixed value
        with patch("time.time", return_value=current_time):
            # Move by 10 pixels (above min_move_distance of 5)
            self.recorder._on_mouse_move(Position(110, 200))

            # Check that event was added
            assert len(self.recorder.events) == 1
            assert isinstance(self.recorder.events[0], MouseMoveEvent)
            assert self.recorder.events[0].position.x == 110
            assert self.recorder.events[0].position.y == 200

            # Last position should be updated
            assert self.recorder.last_recorded_pos.x == 110
            assert self.recorder.last_recorded_pos.y == 200

    def test_on_mouse_move_above_time_threshold(self):
        """Test _on_mouse_move with movement above time threshold."""
        # Setup initial state
        current_time = time.time()
        self.recorder.last_recorded_pos = Position(100, 200)
        self.recorder.last_move_time = (
            current_time - 0.03
        )  # Above min_move_time of 0.02

        # Mock time.time() to return a fixed value
        with patch("time.time", return_value=current_time):
            # Move by 3 pixels (below min_move_distance of 5)
            self.recorder._on_mouse_move(Position(102, 201))

            # Check that event was added due to time threshold
            assert len(self.recorder.events) == 1
            assert isinstance(self.recorder.events[0], MouseMoveEvent)
            assert self.recorder.events[0].position.x == 102
            assert self.recorder.events[0].position.y == 201

    def test_on_mouse_click(self):
        """Test _on_mouse_click method."""
        current_time = time.time()

        # Mock time.time() to return a fixed value
        with patch("time.time", return_value=current_time):
            # Call method for mouse press
            self.recorder._on_mouse_click(Position(100, 200), MouseButton.LEFT, True)

            # Check event was recorded
            assert len(self.recorder.events) == 1
            event = self.recorder.events[0]
            assert isinstance(event, MouseButtonEvent)
            assert event.timestamp == current_time
            assert event.position.x == 100
            assert event.position.y == 200
            assert event.button == MouseButton.LEFT
            assert event.pressed is True

    def test_on_key_event(self):
        """Test _on_key_event method."""
        current_time = time.time()

        # Mock time.time() to return a fixed value
        with patch("time.time", return_value=current_time):
            # Call method for key press
            self.recorder._on_key_event("a", True)

            # Check event was recorded
            assert len(self.recorder.events) == 1
            event = self.recorder.events[0]
            assert isinstance(event, KeyboardEvent)
            assert event.timestamp == current_time
            assert event.key == "a"
            assert event.pressed is True


class TestMacroPlayer:
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Configuration()
        # Mocking screen dimensions to avoid actual screen queries
        self.config.screen_width = 1920
        self.config.screen_height = 1080
        self.config.double_click_threshold = 0.3
        self.config.double_click_distance = 5
        self.config.replay_delay = 0.5

        # Patch dependencies
        self.ui_patcher = patch("src.core.CountdownUI")
        self.output_adapter_patcher = patch("src.core.MouseKeyboardOutputAdapter")
        self.storage_patcher = patch("src.core.MacroStorage")
        self.time_patcher = patch("time.sleep")

        self.mock_ui = self.ui_patcher.start()
        self.mock_output_adapter = self.output_adapter_patcher.start()
        self.mock_storage = self.storage_patcher.start()
        self.mock_time = self.time_patcher.start()

        # Setup mock instances
        self.mock_ui_instance = MagicMock()
        self.mock_output_adapter_instance = MagicMock()

        self.mock_ui.return_value = self.mock_ui_instance
        self.mock_output_adapter.return_value = self.mock_output_adapter_instance

        # Create player
        self.player = MacroPlayer(self.config)

    def teardown_method(self):
        """Tear down test fixtures."""
        self.ui_patcher.stop()
        self.output_adapter_patcher.stop()
        self.storage_patcher.stop()
        self.time_patcher.stop()

    def test_init(self):
        """Test initialization of MacroPlayer."""
        assert self.player.config == self.config
        assert hasattr(self.player, "ui")
        assert hasattr(self.player, "output_adapter")
        assert hasattr(self.player, "last_click_positions")
        assert isinstance(self.player.last_click_positions, dict)

    def test_play(self):
        """Test play method with mock events."""
        # Setup mock events
        mock_events = [
            {
                "action": "move",
                "timestamp": 1000.0,
                "position": [100, 200],
                "time_diff": 0.0,
            },
            {
                "action": "press",
                "timestamp": 1001.0,
                "position": [100, 200],
                "button": "Button.left",
                "time_diff": 1.0,
            },
            {
                "action": "release",
                "timestamp": 1001.5,
                "button": "Button.left",
                "time_diff": 0.5,
            },
            {"action": "scroll", "timestamp": 1002.0, "scroll": 5, "time_diff": 0.5},
            {
                "action": "key",
                "timestamp": 1003.0,
                "key": "a",
                "event_type": "down",
                "time_diff": 1.0,
            },
            {
                "action": "key",
                "timestamp": 1003.5,
                "key": "a",
                "event_type": "up",
                "time_diff": 0.5,
            },
        ]

        self.mock_storage.load_from_file.return_value = mock_events

        # Call the method
        self.player.play("macros/test.json")

        # Verify countdown shown
        self.mock_ui_instance.show_countdown.assert_called_once_with("replay")

        # Verify initial delay
        self.mock_time.assert_any_call(self.config.replay_delay)

        # Verify actions executed
        self.mock_output_adapter_instance.move_mouse.assert_called_once_with(
            ANY, duration=ANY
        )
        self.mock_output_adapter_instance.press_mouse_button.assert_called_once_with(
            MouseButton.LEFT
        )
        self.mock_output_adapter_instance.release_mouse_button.assert_called_once_with(
            MouseButton.LEFT
        )
        self.mock_output_adapter_instance.scroll_mouse.assert_called_once_with(5)
        self.mock_output_adapter_instance.press_key.assert_called_once_with("a")
        self.mock_output_adapter_instance.release_key.assert_called_once_with("a")

    def test_play_file_not_found(self):
        """Test play method with file not found error."""
        # Setup mock to raise error
        self.mock_storage.load_from_file.side_effect = FileNotFoundError()

        # Call the method
        self.player.play("nonexistent.json")

        # Verify countdown not shown
        self.mock_ui_instance.show_countdown.assert_not_called()

        # Verify no actions executed
        self.mock_output_adapter_instance.move_mouse.assert_not_called()

    def test_play_invalid_json(self):
        """Test play method with invalid JSON error."""
        # Setup mock to raise error
        self.mock_storage.load_from_file.side_effect = json.JSONDecodeError("", "", 0)

        # Call the method
        self.player.play("invalid.json")

        # Verify countdown not shown
        self.mock_ui_instance.show_countdown.assert_not_called()

        # Verify no actions executed
        self.mock_output_adapter_instance.move_mouse.assert_not_called()

    def test_check_double_click_true(self):
        """Test _check_double_click method returning True."""
        # Setup
        current_time = time.time()
        self.player.last_click_positions = {
            MouseButton.LEFT: (
                current_time - 0.2,  # Within threshold of 0.3
                Position(100, 200),
            )
        }

        # Call method with position close to last click
        result = self.player._check_double_click(
            MouseButton.LEFT,
            Position(103, 202),  # Within distance threshold of 5
            current_time,
        )

        # Verify result
        assert result is True

    def test_check_double_click_false_time(self):
        """Test _check_double_click method returning False due to time."""
        # Setup
        current_time = time.time()
        self.player.last_click_positions = {
            MouseButton.LEFT: (
                current_time - 0.4,  # Beyond threshold of 0.3
                Position(100, 200),
            )
        }

        # Call method
        result = self.player._check_double_click(
            MouseButton.LEFT, Position(100, 200), current_time  # Same position
        )

        # Verify result
        assert result is False

    def test_check_double_click_false_distance(self):
        """Test _check_double_click method returning False due to distance."""
        # Setup
        current_time = time.time()
        self.player.last_click_positions = {
            MouseButton.LEFT: (
                current_time - 0.2,  # Within threshold of 0.3
                Position(100, 200),
            )
        }

        # Call method with position far from last click
        result = self.player._check_double_click(
            MouseButton.LEFT,
            Position(110, 210),  # Beyond distance threshold of 5
            current_time,
        )

        # Verify result
        assert result is False

    def test_check_double_click_false_no_previous(self):
        """Test _check_double_click method with no previous click."""
        # Setup
        current_time = time.time()
        self.player.last_click_positions = {}  # No previous clicks

        # Call method
        result = self.player._check_double_click(
            MouseButton.LEFT, Position(100, 200), current_time
        )

        # Verify result
        assert result is False
