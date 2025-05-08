from unittest.mock import MagicMock, call, patch

from src.config import Configuration
from src.countdown import CountdownUI


class TestCountdownUI:
    def setup_method(self):
        """Set up test fixtures."""
        # Create a mock configuration
        self.config = Configuration()
        self.config.screen_width = 1920
        self.config.screen_height = 1080
        self.config.countdown_duration = 3
        self.config.countdown_font = "Helvetica"
        self.config.countdown_font_size = 50
        self.config.countdown_background = "white"

        # Create CountdownUI with mock config
        self.countdown_ui = CountdownUI(self.config)

    @patch("time.sleep")
    @patch("src.countdown.Label")  # Patch the actual import in countdown.py
    @patch("src.countdown.Canvas")  # Patch the actual import in countdown.py
    @patch("tkinter.Tk")
    def test_show_countdown_record(self, mock_tk, mock_canvas, mock_label, mock_sleep):
        """Test show_countdown method in record mode."""
        # Setup mock objects
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        mock_canvas_instance = MagicMock()
        mock_canvas.return_value = mock_canvas_instance

        mock_label_instance = MagicMock()
        mock_label.return_value = mock_label_instance

        # Call the method
        self.countdown_ui.show_countdown("record")

        # Verify Tk window setup
        mock_root.attributes.assert_any_call("-transparentcolor", "white")
        mock_root.overrideredirect.assert_called_once_with(1)
        mock_root.geometry.assert_called_once_with("1920x1080+0+0")
        mock_root.attributes.assert_any_call("-topmost", 1)

        # Verify Canvas setup
        mock_canvas.assert_called_once_with(
            mock_root, width=1920, height=1080, bg="white", highlightthickness=0
        )
        mock_canvas_instance.pack.assert_called_once()

        # Verify Label setup
        mock_label.assert_called_once()
        mock_label_instance.place.assert_called_once_with(
            relx=0.5, rely=0.5, anchor="center"
        )

        # Verify countdown
        assert (
            mock_label_instance.config.call_count == 4
        )  # 3 seconds + "Recording has started"
        mock_label_instance.config.assert_has_calls(
            [
                call(text="3"),
                call(text="2"),
                call(text="1"),
                call(text="Recording has started"),
            ]
        )

        # Verify sleep calls
        assert mock_sleep.call_count == 4  # 3 seconds + 1 for final message

        # Verify window destruction
        mock_root.destroy.assert_called_once()

    @patch("time.sleep")
    @patch("src.countdown.Label")  # Patch the actual import in countdown.py
    @patch("src.countdown.Canvas")  # Patch the actual import in countdown.py
    @patch("tkinter.Tk")
    def test_show_countdown_replay(self, mock_tk, mock_canvas, mock_label, mock_sleep):
        """Test show_countdown method in replay mode."""
        # Setup mock objects
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        mock_canvas_instance = MagicMock()
        mock_canvas.return_value = mock_canvas_instance

        mock_label_instance = MagicMock()
        mock_label.return_value = mock_label_instance

        # Call the method
        self.countdown_ui.show_countdown("replay")

        # Verify Canvas setup
        mock_canvas.assert_called_once_with(
            mock_root, width=1920, height=1080, bg="white", highlightthickness=0
        )

        # Verify Label setup
        mock_label.assert_called_once()

        # Verify message is different for replay mode
        mock_label_instance.config.assert_has_calls(
            [
                call(text="3"),
                call(text="2"),
                call(text="1"),
                call(text="Replay has started"),
            ]
        )

        # Verify window destruction
        mock_root.destroy.assert_called_once()

        import pytest


from unittest.mock import MagicMock, call, patch

from src.config import Configuration
from src.io_adapters import (
    KeyboardInputAdapter,
    MouseInputAdapter,
    MouseKeyboardOutputAdapter,
)
from src.models import MouseButton, Position


class TestMouseInputAdapter:
    def setup_method(self):
        """Set up test fixtures."""
        self.on_move = MagicMock()
        self.on_click = MagicMock()
        self.on_scroll = MagicMock()

        self.config = MagicMock()
        self.config.screen_width = 1920
        self.config.screen_height = 1080

        # Create the adapter with mock callbacks
        self.adapter = MouseInputAdapter(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll,
            config=self.config,
        )

    def test_init(self):
        """Test that adapter initializes correctly."""
        assert self.adapter.on_move == self.on_move
        assert self.adapter.on_click == self.on_click
        assert self.adapter.on_scroll == self.on_scroll
        assert self.adapter.config == self.config
        assert self.adapter.listener is None

    @patch("pynput.mouse.Listener")
    def test_start_listening(self, mock_listener_class):
        """Test start_listening method."""
        # Setup mock
        mock_listener = MagicMock()
        mock_listener_class.return_value = mock_listener

        # Call method
        self.adapter.start_listening()

        # Verify listener was created and started
        mock_listener_class.assert_called_once()
        mock_listener.start.assert_called_once()
        assert self.adapter.listener == mock_listener

    @patch("pynput.mouse.Listener")
    def test_start_listening_handles_exception(self, mock_listener_class):
        """Test start_listening handles exceptions."""
        # Setup mock to raise an exception
        mock_listener_class.side_effect = Exception("Test exception")

        # Call method (should not raise the exception)
        self.adapter.start_listening()

        # Verify listener is still None
        assert self.adapter.listener is None

    def test_stop_listening(self):
        """Test stop_listening method."""
        # Setup mock listener
        self.adapter.listener = MagicMock()

        # Call method
        self.adapter.stop_listening()

        # Verify listener was stopped
        self.adapter.listener.stop.assert_called_once()

    def test_stop_listening_no_listener(self):
        """Test stop_listening when no listener exists."""
        # Make sure listener is None
        self.adapter.listener = None

        # Call method (should not raise an exception)
        self.adapter.stop_listening()

    @patch("pynput.mouse.Listener")
    def test_handle_move_in_bounds(self, mock_listener_class):
        """Test the mouse move handler when position is in bounds."""
        # Start listening to create the handler
        self.adapter.start_listening()

        # Extract the move handler from the Listener call
        handler_args = mock_listener_class.call_args[1]
        move_handler = handler_args["on_move"]

        # Call the handler with an in-bounds position
        move_handler(100, 200)

        # Verify our callback was called with the right position
        self.on_move.assert_called_once()
        pos_arg = self.on_move.call_args[0][0]
        assert pos_arg.x == 100
        assert pos_arg.y == 200

    @patch("pynput.mouse.Listener")
    def test_handle_move_out_of_bounds(self, mock_listener_class):
        """Test the mouse move handler when position is out of bounds."""
        # Start listening to create the handler
        self.adapter.start_listening()

        # Extract the move handler from the Listener call
        handler_args = mock_listener_class.call_args[1]
        move_handler = handler_args["on_move"]

        # Call the handler with an out-of-bounds position
        move_handler(2000, 2000)

        # Verify our callback was NOT called
        self.on_move.assert_not_called()

    @patch("pynput.mouse.Listener")
    def test_handle_click_left_button(self, mock_listener_class):
        """Test the mouse click handler with left button."""
        # Create a mock button that will be converted to "Button.left"
        mock_button = MagicMock()
        mock_button.__str__ = lambda self: "Button.left"

        # Start listening to create the handler
        self.adapter.start_listening()

        # Extract the click handler from the Listener call
        handler_args = mock_listener_class.call_args[1]
        click_handler = handler_args["on_click"]

        # Call the handler for press
        click_handler(100, 200, mock_button, True)

        # Verify our callback was called with the right arguments
        self.on_click.assert_called_once()
        args = self.on_click.call_args[0]
        assert args[0].x == 100
        assert args[0].y == 200
        assert args[1] == MouseButton.LEFT
        assert args[2] is True

    @patch("pynput.mouse.Listener")
    def test_handle_click_unknown_button(self, mock_listener_class):
        """Test the mouse click handler with an unknown button."""
        # Create a mock button with an unknown string representation
        mock_button = MagicMock()
        mock_button.__str__ = lambda self: "Button.unknown"

        # Start listening to create the handler
        self.adapter.start_listening()

        # Extract the click handler from the Listener call
        handler_args = mock_listener_class.call_args[1]
        click_handler = handler_args["on_click"]

        # Call the handler
        click_handler(100, 200, mock_button, True)

        # Verify our callback was NOT called
        self.on_click.assert_not_called()

    @patch("pynput.mouse.Listener")
    def test_handle_scroll(self, mock_listener_class):
        """Test the mouse scroll handler."""
        # Start listening to create the handler
        self.adapter.start_listening()

        # Extract the scroll handler from the Listener call
        handler_args = mock_listener_class.call_args[1]
        scroll_handler = handler_args["on_scroll"]

        # Call the handler
        scroll_handler(100, 200, 0, 5)

        # Verify our callback was called with the right arguments
        self.on_scroll.assert_called_once()
        args = self.on_scroll.call_args[0]
        assert args[0].x == 100
        assert args[0].y == 200
        assert args[1] == 5


class TestKeyboardInputAdapter:
    def setup_method(self):
        """Set up test fixtures."""
        self.on_key_event = MagicMock()
        self.adapter = KeyboardInputAdapter(on_key_event=self.on_key_event)

    def test_init(self):
        """Test initialization."""
        assert self.adapter.on_key_event == self.on_key_event

    @patch("keyboard.hook")
    def test_start_listening(self, mock_hook):
        """Test start_listening method."""
        # Call method
        self.adapter.start_listening()

        # Verify hook was called
        mock_hook.assert_called_once()

    @patch("keyboard.unhook_all")
    def test_stop_listening(self, mock_unhook_all):
        """Test stop_listening method."""
        # Call method
        self.adapter.stop_listening()

        # Verify unhook_all was called
        mock_unhook_all.assert_called_once()

    @patch("keyboard.hook")
    def test_handle_key_event(self, mock_hook):
        """Test the key event handler."""
        # Call start_listening to register the handler
        self.adapter.start_listening()

        # Extract the key handler function
        handler = mock_hook.call_args[0][0]

        # Create a mock event
        mock_event = MagicMock()
        mock_event.name = "a"
        mock_event.event_type = "down"

        # Call the handler with the mock event
        handler(mock_event)

        # Verify our callback was called with the right arguments
        self.on_key_event.assert_called_once_with("a", True)

        # Test with key up event
        mock_event.event_type = "up"
        handler(mock_event)
        self.on_key_event.assert_called_with("a", False)


class TestMouseKeyboardOutputAdapter:
    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = MouseKeyboardOutputAdapter()

    @patch("mouse.move")
    def test_move_mouse(self, mock_move):
        """Test move_mouse method."""
        # Call method
        position = Position(100, 200)
        self.adapter.move_mouse(position, duration=0.5)

        # Verify mouse.move was called with right arguments
        mock_move.assert_called_once_with(100, 200, absolute=True, duration=0.5)

    @patch("pyautogui.mouseDown")
    def test_press_mouse_button_left(self, mock_mouse_down):
        """Test press_mouse_button method with left button."""
        # Call method
        self.adapter.press_mouse_button(MouseButton.LEFT)

        # Verify mouseDown was called with right arguments
        mock_mouse_down.assert_called_once_with(button="left")

    @patch("pyautogui.mouseDown")
    def test_press_mouse_button_right(self, mock_mouse_down):
        """Test press_mouse_button method with right button."""
        # Call method
        self.adapter.press_mouse_button(MouseButton.RIGHT)

        # Verify mouseDown was called with right arguments
        mock_mouse_down.assert_called_once_with(button="right")

    @patch("pyautogui.mouseDown")
    def test_press_mouse_button_middle(self, mock_mouse_down):
        """Test press_mouse_button method with middle button."""
        # Call method
        self.adapter.press_mouse_button(MouseButton.MIDDLE)

        # Verify mouseDown was called with right arguments
        mock_mouse_down.assert_called_once_with(button="middle")

    @patch("pyautogui.mouseUp")
    def test_release_mouse_button_left(self, mock_mouse_up):
        """Test release_mouse_button method with left button."""
        # Call method
        self.adapter.release_mouse_button(MouseButton.LEFT)

        # Verify mouseUp was called with right arguments
        mock_mouse_up.assert_called_once_with(button="left")

    @patch("pyautogui.mouseUp")
    def test_release_mouse_button_right(self, mock_mouse_up):
        """Test release_mouse_button method with right button."""
        # Call method
        self.adapter.release_mouse_button(MouseButton.RIGHT)

        # Verify mouseUp was called with right arguments
        mock_mouse_up.assert_called_once_with(button="right")

    @patch("pyautogui.mouseUp")
    def test_release_mouse_button_middle(self, mock_mouse_up):
        """Test release_mouse_button method with middle button."""
        # Call method
        self.adapter.release_mouse_button(MouseButton.MIDDLE)

        # Verify mouseUp was called with right arguments
        mock_mouse_up.assert_called_once_with(button="middle")

    @patch("mouse.wheel")
    def test_scroll_mouse(self, mock_wheel):
        """Test scroll_mouse method."""
        # Call method
        self.adapter.scroll_mouse(5)

        # Verify wheel was called with right arguments
        mock_wheel.assert_called_once_with(delta=5)

    @patch("keyboard.press")
    def test_press_key(self, mock_press):
        """Test press_key method."""
        # Call method
        self.adapter.press_key("a")

        # Verify press was called with right arguments
        mock_press.assert_called_once_with("a")

    @patch("keyboard.release")
    def test_release_key(self, mock_release):
        """Test release_key method."""
        # Call method
        self.adapter.release_key("a")

        # Verify release was called with right arguments
        mock_release.assert_called_once_with("a")
