from unittest.mock import patch

import pytest

from src.config import Configuration, DisplayManager


class TestConfiguration:
    def test_default_values(self):
        """Test that Configuration class initializes with expected default values."""
        with patch("src.config.DisplayManager.get_screen_width", return_value=1920):
            with patch(
                "src.config.DisplayManager.get_screen_height", return_value=1080
            ):
                config = Configuration()

                # Check screen dimensions
                assert config.screen_width == 1920
                assert config.screen_height == 1080

                # Check default settings
                assert config.min_move_distance == 5
                assert config.min_move_time == 0.02
                assert config.double_click_threshold == 0.3
                assert config.double_click_distance == 5
                assert config.countdown_duration == 3
                assert config.countdown_font == "Helvetica"
                assert config.countdown_font_size == 50
                assert config.countdown_background == "white"
                assert config.replay_delay == 0.5


class TestDisplayManager:

    @pytest.mark.skip
    def test_get_screen_width(self):
        """Test get_screen_width method."""
        with patch("pyautogui.size", return_value=(1920, 1080)):
            assert DisplayManager.get_screen_width() == 1920

    @pytest.mark.skip
    def test_get_screen_height(self):
        """Test get_screen_height method."""
        with patch("pyautogui.size", return_value=(1920, 1080)):
            assert DisplayManager.get_screen_height() == 1080

    @pytest.mark.skip
    def test_set_cursor_position_windows(self):
        """Test set_cursor_position on Windows platform."""
        with patch("platform.system", return_value="Windows"):
            with patch("ctypes.windll.user32.SetCursorPos") as mock_set_cursor:
                DisplayManager.set_cursor_position(100, 200)
                mock_set_cursor.assert_called_once_with(100, 200)

    @pytest.mark.skip
    def test_set_cursor_position_other(self):
        """Test set_cursor_position on non-Windows platform."""
        with patch("platform.system", return_value="Linux"):
            with patch("pyautogui.moveTo") as mock_move_to:
                DisplayManager.set_cursor_position(100, 200)
                mock_move_to.assert_called_once_with(100, 200)


import platform
from unittest.mock import MagicMock, patch

# Existing imports in src.config
import pyautogui
import pytest

from src.config import Configuration, DisplayManager, logger

# Assign pyautogui as an attribute if needed
pyautogui = pyautogui


class TestConfiguration:
    """Tests for the Configuration class."""

    def test_default_initialization(self):
        """Test that Configuration class initializes with expected default values."""
        with patch("src.config.DisplayManager.get_screen_width", return_value=1920):
            with patch(
                "src.config.DisplayManager.get_screen_height", return_value=1080
            ):
                config = Configuration()

                # Check screen dimensions
                assert config.screen_width == 1920
                assert config.screen_height == 1080

                # Check default settings
                assert config.min_move_distance == 5
                assert config.min_move_time == 0.02
                assert config.double_click_threshold == 0.3
                assert config.double_click_distance == 5
                assert config.countdown_duration == 3
                assert config.countdown_font == "Helvetica"
                assert config.countdown_font_size == 50
                assert config.countdown_background == "white"
                assert config.replay_delay == 0.5

    def test_custom_initialization(self):
        """Test that Configuration can be initialized with custom values."""
        config = Configuration(
            screen_width=3840,
            screen_height=2160,
            min_move_distance=10,
            min_move_time=0.05,
            double_click_threshold=0.5,
            double_click_distance=10,
            countdown_duration=5,
            countdown_font="Arial",
            countdown_font_size=100,
            countdown_background="black",
            replay_delay=1.0,
        )

        assert config.screen_width == 3840
        assert config.screen_height == 2160
        assert config.min_move_distance == 10
        assert config.min_move_time == 0.05
        assert config.double_click_threshold == 0.5
        assert config.double_click_distance == 10
        assert config.countdown_duration == 5
        assert config.countdown_font == "Arial"
        assert config.countdown_font_size == 100
        assert config.countdown_background == "black"
        assert config.replay_delay == 1.0


class TestDisplayManager:
    """Tests for the DisplayManager class."""

    def test_get_screen_width_success(self):
        """Test get_screen_width method when pyautogui succeeds."""
        mock_size = (1920, 1080)
        with patch("pyautogui.size", return_value=mock_size):
            result = DisplayManager.get_screen_width()
            assert result == 1920

    def test_get_screen_width_failure(self):
        """Test get_screen_width method when pyautogui fails."""
        with patch("pyautogui.size", side_effect=Exception("Test exception")):
            result = DisplayManager.get_screen_width()
            assert result == 1920  # Should return fallback value

    def test_get_screen_height_success(self):
        """Test get_screen_height method when pyautogui succeeds."""
        mock_size = (1920, 1080)
        with patch("pyautogui.size", return_value=mock_size):
            result = DisplayManager.get_screen_height()
            assert result == 1080

    def test_get_screen_height_failure(self):
        """Test get_screen_height method when pyautogui fails."""
        with patch("pyautogui.size", side_effect=Exception("Test exception")):
            result = DisplayManager.get_screen_height()
            assert result == 1080  # Should return fallback value

    def test_set_cursor_position_windows(self):
        """Test set_cursor_position on Windows platform."""
        with patch("platform.system", return_value="Windows"):
            with patch("ctypes.windll.user32.SetCursorPos") as mock_set_cursor:
                DisplayManager.set_cursor_position(100, 200)
                mock_set_cursor.assert_called_once_with(100, 200)

    @pytest.mark.skip()
    def test_set_cursor_position_non_windows(self):
        """Test set_cursor_position on non-Windows platform."""
        with patch("platform.system", return_value="Linux"):
            with patch("pyautogui.moveTo") as mock_move_to:
                DisplayManager.set_cursor_position(100, 200)
                mock_move_to.assert_called_once_with(100, 200)

    @pytest.mark.skip()
    @patch("src.config.pyautogui")
    @patch("platform.system")
    @patch("ctypes.windll.user32.SetCursorPos")
    def test_set_cursor_position_platform_specific(
        self, mock_set_cursor, mock_system, mock_pyautogui
    ):
        """Test set_cursor_position with different platform values."""
        # Test Windows
        mock_system.return_value = "Windows"
        DisplayManager.set_cursor_position(100, 200)
        mock_set_cursor.assert_called_once_with(100, 200)
        mock_pyautogui.moveTo.assert_not_called()

        # Reset mocks
        mock_set_cursor.reset_mock()
        mock_pyautogui.moveTo.reset_mock()

        # Test non-Windows
        mock_system.return_value = "Darwin"  # macOS
        DisplayManager.set_cursor_position(300, 400)
        mock_set_cursor.assert_not_called()
        mock_pyautogui.moveTo.assert_called_once_with(300, 400)


def test_logger_configuration():
    """Test that logger is properly configured."""
    assert logger.name == "macro_recorder"
    assert logger.level <= 20  # INFO level or lower (more detailed)
