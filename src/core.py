import json
import random
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

from src.config import Configuration, logger
from src.countdown import CountdownUI
from src.io_adapters import (
    KeyboardInputAdapter,
    MouseInputAdapter,
    MouseKeyboardOutputAdapter,
)
from src.models import (
    KeyboardEvent,
    MacroEvent,
    MouseButton,
    MouseButtonEvent,
    MouseMoveEvent,
    MouseScrollEvent,
    Position,
)
from src.storage import MacroStorage


class MacroRecorder:
    """Records mouse and keyboard actions."""

    def __init__(self, config: Configuration = None):
        """Initialize with optional configuration."""
        self.config = config or Configuration()
        self.events: List[MacroEvent] = []
        self.ui = CountdownUI(self.config)

        # State for throttling mouse movements
        self.last_recorded_pos: Optional[Position] = None
        self.last_move_time: float = 0.0

        # Thread safety
        self.lock = threading.Lock()

        # Input adapters
        self.mouse_adapter = MouseInputAdapter(
            on_move=self._on_mouse_move,
            on_click=self._on_mouse_click,
            on_scroll=self._on_mouse_scroll,
            config=self.config,
        )
        self.keyboard_adapter = KeyboardInputAdapter(on_key_event=self._on_key_event)

    def _on_mouse_move(self, position: Position) -> None:
        """
        Handle mouse movement event.

        Args:
            position: The new mouse position
        """
        current_time = time.time()

        # Initialize last_recorded_pos if not set
        if self.last_recorded_pos is None:
            self.last_recorded_pos = position
            self.last_move_time = current_time
            return

        # Throttle mouse movements by distance and time
        distance = position.distance_to(self.last_recorded_pos)
        time_diff = current_time - self.last_move_time

        # Only record if moved enough or enough time passed
        if (
            distance > self.config.min_move_distance
            or time_diff > self.config.min_move_time
        ):

            with self.lock:
                self.events.append(
                    MouseMoveEvent(timestamp=current_time, position=position)
                )

            self.last_recorded_pos = position
            self.last_move_time = current_time

    def _on_mouse_click(
        self, position: Position, button: MouseButton, pressed: bool
    ) -> None:
        """
        Handle mouse click event.

        Args:
            position: The mouse position
            button: The mouse button
            pressed: True if pressed, False if released
        """
        with self.lock:
            self.events.append(
                MouseButtonEvent(
                    timestamp=time.time(),
                    position=position,
                    button=button,
                    pressed=pressed,
                )
            )

    def _on_mouse_scroll(self, position: Position, amount: int) -> None:
        """
        Handle mouse scroll event.

        Args:
            position: The mouse position
            amount: The scroll amount
        """
        with self.lock:
            self.events.append(
                MouseScrollEvent(
                    timestamp=time(), position=position, scroll_amount=amount
                )
            )

    def _on_key_event(self, key: str, pressed: bool) -> None:
        """
        Handle keyboard event.

        Args:
            key: The key name
            pressed: True if pressed, False if released
        """
        with self.lock:
            self.events.append(
                KeyboardEvent(timestamp=time.time(), key=key, pressed=pressed)
            )

    def start_recording(self) -> None:
        """Start recording mouse and keyboard actions."""
        self.ui.show_countdown("record")
        logger.info("Recording started. Press Ctrl+C to stop.")

        # Reset state
        self.events = []
        self.last_recorded_pos = None
        self.last_move_time = 0.0

        # Start input adapters
        self.mouse_adapter.start_listening()
        self.keyboard_adapter.start_listening()

    def stop_recording(self) -> None:
        """Stop recording and return events."""
        self.mouse_adapter.stop_listening()
        self.keyboard_adapter.stop_listening()
        logger.info(f"Recording stopped. Recorded {len(self.events)} events.")

    def save_recording(self, filename: str) -> None:
        """Save recorded events to a file."""
        if not self.events:
            logger.warning("No events to save.")
            return

        MacroStorage.save_to_file(self.events, filename)


class MacroPlayer:
    """Plays back recorded mouse and keyboard actions."""

    def __init__(self, config: Configuration = None):
        """Initialize with optional configuration."""
        self.config = config or Configuration()
        self.ui = CountdownUI(self.config)
        self.output_adapter = MouseKeyboardOutputAdapter()

        # State for double-click detection
        self.last_click_positions: Dict[MouseButton, Tuple[float, Position]] = {}

    def play(self, filename: str, speed_factor: float = 1.0) -> None:
        """
        Play back recorded actions from a file.

        Args:
            filename: Path to the file
            speed_factor: Speed multiplier (default: 1.0)
        """
        try:
            events = MacroStorage.load_from_file(filename)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load macro file: {e}")
            return

        self.ui.show_countdown("replay")
        logger.info(f"Replaying {len(events)} events at {speed_factor}x speed...")

        # Wait a moment before starting replay
        time.sleep(self.config.replay_delay)

        # Initialize timing variables
        start_time = time.time()
        last_action_time = start_time

        # Reset double-click state
        self.last_click_positions = {}

        # Process events
        skip_count = 0
        for i, event_dict in enumerate(events):
            action = event_dict["action"]

            # Only consider skipping mouse movements
            # This is how the speed factor is implemented.
            if speed_factor > 1 and action == "move":
                # Simple approach: skip some percentage of mouse movements
                # but never skip consecutive movements more than X times
                if skip_count < min(5, speed_factor) and random.random() < (
                    1 - 1 / speed_factor
                ):
                    skip_count += 1
                    continue
                skip_count = 0

            # Calculate timing
            if i > 0:
                # Use time_diff for timing between actions
                time_diff = event_dict["time_diff"] / speed_factor

                # Wait for the appropriate time
                wait_time = max(0, time_diff - (time.time() - last_action_time))
                if wait_time > 0:
                    time.sleep(wait_time)

            # Remember when this action started
            last_action_time = time.time()

            # Determine event type and execute
            self._execute_event(event_dict, last_action_time)

        logger.info("Replay complete.")

    def _execute_event(self, event_dict: Dict[str, Any], current_time: float) -> None:
        """
        Execute a single event.

        Args:
            event_dict: The event dictionary
            current_time: The current timestamp
        """
        action = event_dict["action"]

        if action == "move":
            position = Position(event_dict["position"][0], event_dict["position"][1])
            self.output_adapter.move_mouse(position, duration=0.01)

        elif action == "press":
            position = Position(event_dict["position"][0], event_dict["position"][1])
            button = MouseButton.from_string(event_dict["button"])

            # Check for double click
            is_double_click = self._check_double_click(button, position, current_time)
            if is_double_click:
                logger.info(f"Double {button.name} click detected")

            # Remember this click
            self.last_click_positions[button] = (current_time, position)

            # Perform the click
            self.output_adapter.press_mouse_button(button)

        elif action == "release":
            button = MouseButton.from_string(event_dict["button"])
            self.output_adapter.release_mouse_button(button)

        elif action == "scroll":
            self.output_adapter.scroll_mouse(event_dict["scroll"])

        elif action == "key":
            key = event_dict["key"]
            if event_dict["event_type"] == "down":
                self.output_adapter.press_key(key)
            elif event_dict["event_type"] == "up":
                self.output_adapter.release_key(key)

    def _check_double_click(
        self, button: MouseButton, position: Position, current_time: float
    ) -> bool:
        """
        Check if this is a double click.

        Args:
            button: The mouse button
            position: The current position
            current_time: The current timestamp

        Returns:
            True if this is a double click, False otherwise
        """
        if button in self.last_click_positions:
            last_time, last_pos = self.last_click_positions[button]
            time_since_last = current_time - last_time

            # Calculate distance from last click
            distance = position.distance_to(last_pos)

            if (
                time_since_last < self.config.double_click_threshold
                and distance < self.config.double_click_distance
            ):
                return True

        return False
