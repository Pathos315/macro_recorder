import pytest


@pytest.fixture(autouse=True)
def mock_display_manager(monkeypatch):
    """Mock DisplayManager methods to return fixed values in tests."""
    from src.config import DisplayManager

    monkeypatch.setattr(DisplayManager, "get_screen_width", lambda: 1920)
    monkeypatch.setattr(DisplayManager, "get_screen_height", lambda: 1080)
