# Create a mock Configuration class for tests
from unittest.mock import patch

import pytest

from src.config import Configuration


@pytest.fixture
def mock_config():
    with patch("src.config.DisplayManager.get_screen_width", return_value=1920):
        with patch("src.config.DisplayManager.get_screen_height", return_value=1080):
            config = Configuration()
            config.screen_width = 1920
            config.screen_height = 1080
            yield config
