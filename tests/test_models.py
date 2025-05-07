import pytest
from src.models import Position, MouseButton
from src.models import MouseMoveEvent, MouseButtonEvent, MouseScrollEvent, KeyboardEvent


class TestPosition:
    def test_init(self):
        """Test Position initialization."""
        pos = Position(100, 200)
        assert pos.x == 100
        assert pos.y == 200

    def test_str_representation(self):
        """Test string representation of Position."""
        pos = Position(100, 200)
        assert str(pos) == "(100, 200)"

    def test_distance_to(self):
        """Test distance calculation between positions."""
        pos1 = Position(0, 0)
        pos2 = Position(3, 4)
        # Pythagorean theorem: sqrt(3^2 + 4^2) = 5
        assert pos1.distance_to(pos2) == 5.0


class TestMouseButton:
    def test_from_string_valid(self):
        """Test from_string with valid inputs."""
        assert MouseButton.from_string("Button.left") == MouseButton.LEFT
        assert MouseButton.from_string("Button.right") == MouseButton.RIGHT
        assert MouseButton.from_string("Button.middle") == MouseButton.MIDDLE

    def test_from_string_invalid(self):
        """Test from_string with invalid input."""
        with pytest.raises(ValueError):
            MouseButton.from_string("Button.invalid")


class TestMouseMoveEvent:
    def test_to_dict(self):
        """Test conversion to dictionary."""
        timestamp = 1234567890.123
        pos = Position(100, 200)
        event = MouseMoveEvent(timestamp=timestamp, position=pos)

        expected_dict = {
            "action": "move",
            "timestamp": timestamp,
            "position": (100, 200),
        }

        assert event.to_dict() == expected_dict

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {"action": "move", "timestamp": 1234567890.123, "position": (100, 200)}

        event = MouseMoveEvent.from_dict(data)

        assert event.timestamp == 1234567890.123
        assert event.position.x == 100
        assert event.position.y == 200


class TestMouseButtonEvent:
    def test_to_dict_press(self):
        """Test conversion to dictionary for press event."""
        timestamp = 1234567890.123
        pos = Position(100, 200)
        button = MouseButton.LEFT
        event = MouseButtonEvent(
            timestamp=timestamp, position=pos, button=button, pressed=True
        )

        expected_dict = {
            "action": "press",
            "timestamp": timestamp,
            "button": "Button.left",
            "position": (100, 200),
        }

        assert event.to_dict() == expected_dict

    def test_to_dict_release(self):
        """Test conversion to dictionary for release event."""
        timestamp = 1234567890.123
        pos = Position(100, 200)
        button = MouseButton.LEFT
        event = MouseButtonEvent(
            timestamp=timestamp, position=pos, button=button, pressed=False
        )

        expected_dict = {
            "action": "release",
            "timestamp": timestamp,
            "button": "Button.left",
            "position": (100, 200),
        }

        assert event.to_dict() == expected_dict

    def test_from_dict_press(self):
        """Test creation from dictionary for press event."""
        data = {
            "action": "press",
            "timestamp": 1234567890.123,
            "button": "Button.left",
            "position": (100, 200),
        }

        event = MouseButtonEvent.from_dict(data)

        assert event.timestamp == 1234567890.123
        assert event.position.x == 100
        assert event.position.y == 200
        assert event.button == MouseButton.LEFT
        assert event.pressed is True

    def test_from_dict_release(self):
        """Test creation from dictionary for release event."""
        data = {
            "action": "release",
            "timestamp": 1234567890.123,
            "button": "Button.left",
            "position": (100, 200),
        }

        event = MouseButtonEvent.from_dict(data)

        assert event.timestamp == 1234567890.123
        assert event.position.x == 100
        assert event.position.y == 200
        assert event.button == MouseButton.LEFT
        assert event.pressed is False


class TestMouseScrollEvent:
    def test_to_dict(self):
        """Test conversion to dictionary."""
        timestamp = 1234567890.123
        pos = Position(100, 200)
        scroll_amount = 5
        event = MouseScrollEvent(
            timestamp=timestamp, position=pos, scroll_amount=scroll_amount
        )

        expected_dict = {
            "action": "scroll",
            "timestamp": timestamp,
            "position": (100, 200),
            "scroll": 5,
        }

        assert event.to_dict() == expected_dict

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "action": "scroll",
            "timestamp": 1234567890.123,
            "position": (100, 200),
            "scroll": 5,
        }

        event = MouseScrollEvent.from_dict(data)

        assert event.timestamp == 1234567890.123
        assert event.position.x == 100
        assert event.position.y == 200
        assert event.scroll_amount == 5


class TestKeyboardEvent:
    def test_to_dict_key_down(self):
        """Test conversion to dictionary for key down event."""
        timestamp = 1234567890.123
        key = "a"
        event = KeyboardEvent(timestamp=timestamp, key=key, pressed=True)

        expected_dict = {
            "action": "key",
            "timestamp": timestamp,
            "key": "a",
            "event_type": "down",
        }

        assert event.to_dict() == expected_dict

    def test_to_dict_key_up(self):
        """Test conversion to dictionary for key up event."""
        timestamp = 1234567890.123
        key = "a"
        event = KeyboardEvent(timestamp=timestamp, key=key, pressed=False)

        expected_dict = {
            "action": "key",
            "timestamp": timestamp,
            "key": "a",
            "event_type": "up",
        }

        assert event.to_dict() == expected_dict

    def test_from_dict_key_down(self):
        """Test creation from dictionary for key down event."""
        data = {
            "action": "key",
            "timestamp": 1234567890.123,
            "key": "a",
            "event_type": "down",
        }

        event = KeyboardEvent.from_dict(data)

        assert event.timestamp == 1234567890.123
        assert event.key == "a"
        assert event.pressed is True

    def test_from_dict_key_up(self):
        """Test creation from dictionary for key up event."""
        data = {
            "action": "key",
            "timestamp": 1234567890.123,
            "key": "a",
            "event_type": "up",
        }

        event = KeyboardEvent.from_dict(data)

        assert event.timestamp == 1234567890.123
        assert event.key == "a"
        assert event.pressed is False
