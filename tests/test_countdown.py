import unittest
from unittest.mock import patch, MagicMock
from src.config import Configuration
from src.countdown import CountdownUI


class TestCountdownUI(unittest.TestCase):
    """Tests for the CountdownUI class."""

    def setUp(self):
        """Set up test fixtures before each test method is run."""
        config = Configuration()
        # Override screen dimensions for consistent testing
        config.screen_width = 1920
        config.screen_height = 1080
        config.countdown_duration = 3
        config.countdown_font = "Helvetica"
        config.countdown_font_size = 50
        config.countdown_background = "white"
        self.countdown_ui = CountdownUI(config)

    @patch("time.sleep")
    @patch("tkinter.Label")
    @patch("tkinter.Canvas")
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

        # Call the method - with patch applied at import level
        with patch("src.countdown.Canvas", mock_canvas):
            with patch("src.countdown.Label", mock_label):
                self.countdown_ui.show_countdown("record")

        # Verify Tk window setup
        mock_root.attributes.assert_any_call("-transparentcolor", "white")
        mock_root.overrideredirect.assert_called_once_with(1)
        mock_root.geometry.assert_called_once_with("1920x1080+0+0")
        mock_root.attributes.assert_any_call("-topmost", 1)

        # Verify Canvas setup - Note: Now using the directly imported Canvas mock
        mock_canvas.assert_called_once_with(
            mock_root, width=1920, height=1080, bg="white", highlightthickness=0
        )

        # Verify Canvas instance methods
        mock_canvas_instance.pack.assert_called_once()

        # Verify Label setup
        mock_label.assert_called_once_with(
            mock_canvas_instance, text="", font=("Helvetica", 50)
        )

        # Verify Label instance methods
        mock_label_instance.place.assert_called_once_with(
            relx=0.5, rely=0.5, anchor="center"
        )

        # Verify the countdown behavior
        self.assertEqual(
            mock_label_instance.config.call_count, 4
        )  # 3 countdown + 1 final message
        mock_sleep.assert_called()

        # Verify window cleanup
        mock_root.destroy.assert_called_once()

    @patch("time.sleep")
    @patch("tkinter.Label")
    @patch("tkinter.Canvas")
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

        # Call the method - with patch applied at import level
        with patch("src.countdown.Canvas", mock_canvas):
            with patch("src.countdown.Label", mock_label):
                self.countdown_ui.show_countdown("replay")

        # Verify Tk window setup
        mock_root.attributes.assert_any_call("-transparentcolor", "white")
        mock_root.overrideredirect.assert_called_once_with(1)
        mock_root.geometry.assert_called_once_with("1920x1080+0+0")
        mock_root.attributes.assert_any_call("-topmost", 1)

        # Verify Canvas setup
        mock_canvas.assert_called_once_with(
            mock_root, width=1920, height=1080, bg="white", highlightthickness=0
        )

        # Verify Canvas instance methods
        mock_canvas_instance.pack.assert_called_once()

        # Verify Label setup
        mock_label.assert_called_once_with(
            mock_canvas_instance, text="", font=("Helvetica", 50)
        )

        # Verify Label instance methods
        mock_label_instance.place.assert_called_once_with(
            relx=0.5, rely=0.5, anchor="center"
        )

        # Verify the countdown behavior
        self.assertEqual(
            mock_label_instance.config.call_count, 4
        )  # 3 countdown + 1 final message
        mock_sleep.assert_called()

        # Verify final message shows "Replay has started"
        final_call_args = mock_label_instance.config.call_args_list[-1][1]
        self.assertEqual(final_call_args.get("text"), "Replay has started")

        # Verify window cleanup
        mock_root.destroy.assert_called_once()
