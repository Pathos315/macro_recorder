from unittest.mock import patch

from main import main


def test_main_calls_cli_run():
    """Test that main calls the run method of MacroRecorderCLI."""
    with patch("main.MacroRecorderCLI") as MockMacroRecorderCLI:
        mock_cli_instance = MockMacroRecorderCLI.return_value
        main()
        MockMacroRecorderCLI.assert_called_once()
        mock_cli_instance.run.assert_called_once()
