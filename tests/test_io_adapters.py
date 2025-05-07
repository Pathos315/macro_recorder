from unittest.mock import patch, MagicMock, call
from src.countdown import CountdownUI
from src.config import Configuration


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
