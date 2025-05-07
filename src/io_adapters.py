from typing import Any, Callable, Protocol, runtime_checkable

from src.config import Configuration, logger
from src.models import MouseButton, Position


@runtime_checkable
class InputAdapter(Protocol):
    """Protocol for input adapters."""

    def start_listening(self) -> None:
        """Start listening for input events."""
        ...

    def stop_listening(self) -> None:
        """Stop listening for input events."""
        ...


class MouseInputAdapter(InputAdapter):
    """Adapter for mouse input using pynput."""

    def __init__(
        self,
        on_move: Callable[[Position], None],
        on_click: Callable[[Position, MouseButton, bool], None],
        on_scroll: Callable[[Position, int], None],
        config: Configuration,
    ):
        """Initialize with callback functions and configuration."""
        self.on_move = on_move
        self.on_click = on_click
        self.on_scroll = on_scroll
        self.config = config
        self.listener = None

    def start_listening(self) -> None:
        """Start listening for mouse events."""
        from pynput import mouse as pynput_mouse

        def handle_move(x: int, y: int) -> None:
            """Handle mouse movement event."""
            if 0 <= x < self.config.screen_width and 0 <= y < self.config.screen_height:
                self.on_move(Position(x, y))

        def handle_click(x: int, y: int, button: Any, pressed: bool) -> None:
            """Handle mouse click event."""
            if 0 <= x < self.config.screen_width and 0 <= y < self.config.screen_height:
                # Convert pynput button to our MouseButton enum
                try:
                    button_str = str(button)
                    mouse_button = MouseButton.from_string(button_str)
                    self.on_click(Position(x, y), mouse_button, pressed)
                except ValueError:
                    logger.warning(f"Unknown mouse button: {button}")

        def handle_scroll(x: int, y: int, dx: int, dy: int) -> None:
            """Handle mouse scroll event."""
            if 0 <= x < self.config.screen_width and 0 <= y < self.config.screen_height:
                self.on_scroll(Position(x, y), dy)

        self.listener = pynput_mouse.Listener(
            on_move=handle_move, on_click=handle_click, on_scroll=handle_scroll
        )
        self.listener.start()
        logger.info("Mouse input adapter started")

    def stop_listening(self) -> None:
        """Stop listening for mouse events."""
        if self.listener:
            self.listener.stop()
            logger.info("Mouse input adapter stopped")


class KeyboardInputAdapter(InputAdapter):
    """Adapter for keyboard input using keyboard_hooks."""

    def __init__(self, on_key_event: Callable[[str, bool], None]):
        """Initialize with callback function."""
        self.on_key_event = on_key_event

    def start_listening(self) -> None:
        """Start listening for keyboard events."""
        import keyboard as keyboard_hooks

        def handle_key_event(e) -> None:
            """Handle keyboard event."""
            self.on_key_event(e.name, e.event_type == "down")

        keyboard_hooks.hook(handle_key_event)
        logger.info("Keyboard input adapter started")

    def stop_listening(self) -> None:
        """Stop listening for keyboard events."""
        import keyboard as keyboard_hooks

        keyboard_hooks.unhook_all()
        logger.info("Keyboard input adapter stopped")


@runtime_checkable
class OutputAdapter(Protocol):
    """Abstract base class for output adapters."""

    def move_mouse(self, position: Position, duration: float = 0.0) -> None:
        """Move the mouse to a position."""
        ...

    def press_mouse_button(self, button: MouseButton) -> None:
        """Press a mouse button."""
        ...

    def release_mouse_button(self, button: MouseButton) -> None:
        """Release a mouse button."""
        ...

    def scroll_mouse(self, amount: int) -> None:
        """Scroll the mouse wheel."""
        ...

    def press_key(self, key: str) -> None:
        """Press a keyboard key."""
        ...

    def release_key(self, key: str) -> None:
        """Release a keyboard key."""
        ...


class MouseKeyboardOutputAdapter(OutputAdapter):
    """Adapter for mouse and keyboard output using pyautogui and keyboard_hooks."""

    def move_mouse(self, position: Position, duration: float = 0.0) -> None:
        """Move the mouse to a position."""
        import mouse

        mouse.move(position.x, position.y, absolute=True, duration=duration)
        logger.debug(f"Mouse moved to {position}")

    def press_mouse_button(self, button: MouseButton) -> None:
        """Press a mouse button."""
        import pyautogui

        if button == MouseButton.LEFT:
            pyautogui.mouseDown(button="left")
            logger.debug("Left mouse button pressed")
        elif button == MouseButton.RIGHT:
            pyautogui.mouseDown(button="right")
            logger.debug("Right mouse button pressed")
        elif button == MouseButton.MIDDLE:
            pyautogui.mouseDown(button="middle")
            logger.debug("Middle mouse button pressed")

    def release_mouse_button(self, button: MouseButton) -> None:
        """Release a mouse button."""
        import pyautogui

        if button == MouseButton.LEFT:
            pyautogui.mouseUp(button="left")
            logger.debug("Left mouse button released")
        elif button == MouseButton.RIGHT:
            pyautogui.mouseUp(button="right")
            logger.debug("Right mouse button released")
        elif button == MouseButton.MIDDLE:
            pyautogui.mouseUp(button="middle")
            logger.debug("Middle mouse button released")

    def scroll_mouse(self, amount: int) -> None:
        """Scroll the mouse wheel."""
        import mouse

        mouse.wheel(delta=amount)
        logger.debug(f"Mouse scrolled by {amount}")

    def press_key(self, key: str) -> None:
        """Press a keyboard key."""
        import keyboard as keyboard_hooks

        keyboard_hooks.press(key)
        logger.debug(f"Key pressed: {key}")

    def release_key(self, key: str) -> None:
        """Release a keyboard key."""
        import keyboard as keyboard_hooks

        keyboard_hooks.release(key)
        logger.debug(f"Key released: {key}")
