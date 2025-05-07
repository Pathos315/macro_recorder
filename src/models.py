from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict


class EventType(Enum):
    """Enumeration of event types for clarity and type safety."""

    MOVE = auto()
    PRESS = auto()
    RELEASE = auto()
    SCROLL = auto()
    KEY_DOWN = auto()
    KEY_UP = auto()


@dataclass(frozen=True)
class Position:
    """Immutable value object representing a screen position."""

    x: int
    y: int

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def distance_to(self, other: "Position") -> float:
        """Calculate Euclidean distance to another position."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


class MouseButton(Enum):
    """Enumeration of mouse buttons for clarity and type safety."""

    LEFT = "Button.left"
    RIGHT = "Button.right"
    MIDDLE = "Button.middle"

    @staticmethod
    def from_string(button_str: str) -> "MouseButton":
        """Convert a button string to a MouseButton enum value."""
        for button in MouseButton:
            if button.value == button_str:
                return button
        raise ValueError(f"Unknown mouse button: {button_str}")


@dataclass(frozen=True)
class MacroEvent:
    """Base class for all macro events."""

    timestamp: float

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to a dictionary for serialization."""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MacroEvent":
        """Create an event from a dictionary."""
        pass


@dataclass(frozen=True)
class MouseMoveEvent(MacroEvent):
    """Event representing a mouse movement."""

    position: Position

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": "move",
            "timestamp": self.timestamp,
            "position": (self.position.x, self.position.y),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MouseMoveEvent":
        return cls(
            timestamp=data["timestamp"],
            position=Position(data["position"][0], data["position"][1]),
        )


@dataclass(frozen=True)
class MouseButtonEvent(MacroEvent):
    """Event representing a mouse button press or release."""

    button: MouseButton
    position: Position
    pressed: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": "press" if self.pressed else "release",
            "timestamp": self.timestamp,
            "button": self.button.value,
            "position": (self.position.x, self.position.y),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MouseButtonEvent":
        return cls(
            timestamp=data["timestamp"],
            button=MouseButton.from_string(data["button"]),
            position=Position(data["position"][0], data["position"][1]),
            pressed=data["action"] == "press",
        )


@dataclass(frozen=True)
class MouseScrollEvent(MacroEvent):
    """Event representing a mouse scroll."""

    position: Position
    scroll_amount: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": "scroll",
            "timestamp": self.timestamp,
            "position": (self.position.x, self.position.y),
            "scroll": self.scroll_amount,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MouseScrollEvent":
        return cls(
            timestamp=data["timestamp"],
            position=Position(data["position"][0], data["position"][1]),
            scroll_amount=data["scroll"],
        )


@dataclass(frozen=True)
class KeyboardEvent(MacroEvent):
    """Event representing a keyboard key press or release."""

    key: str
    pressed: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": "key",
            "timestamp": self.timestamp,
            "key": self.key,
            "event_type": "down" if self.pressed else "up",
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KeyboardEvent":
        return cls(
            timestamp=data["timestamp"],
            key=data["key"],
            pressed=data["event_type"] == "down",
        )
