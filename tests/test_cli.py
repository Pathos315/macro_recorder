from unittest.mock import patch, MagicMock
import argparse
from ..cli import MacroRecorderCLI, main


class TestMacroRecorderCLI:
    def setup_method(self):
        """Set up test fixtures."""
        # Patch dependencies
        self.config_patcher = patch("src.cli.Configuration")
        self.recorder_patcher = patch("src.cli.MacroRecorder")
        self.player_patcher = patch("src.cli.MacroPlayer")

        self.mock_config = self.config_patcher.start()
        self.mock_recorder = self.recorder_patcher.start()
        self.mock_player = self.player_patcher.start()

        # Setup mock instances
        self.mock_config_instance = MagicMock()
        self.mock_recorder_instance = MagicMock()
        self.mock_player_instance = MagicMock()

        self.mock_config.return_value = self.mock_config_instance
        self.mock_recorder.return_value = self.mock_recorder_instance
        self.mock_player.return_value = self.mock_player_instance

        # Create CLI instance
        self.cli = MacroRecorderCLI()

    def teardown_method(self):
        """Tear down test fixtures."""
        self.config_patcher.stop()
        self.recorder_patcher.stop()
        self.player_patcher.stop()

    def test_init(self):
        """Test initialization of MacroRecorderCLI."""
        assert hasattr(self.cli, "config")
        assert hasattr(self.cli, "recorder")
        assert hasattr(self.cli, "player")

        # Verify instances created
        self.mock_config.assert_called_once()
        self.mock_recorder.assert_called_once_with(self.mock_config_instance)
        self.mock_player.assert_called_once_with(self.mock_config_instance)

    @patch("argparse.ArgumentParser.parse_args")
    def test_parse_arguments_record(self, mock_parse_args):
        """Test parse_arguments method with record command."""
        # Setup mock return value
        mock_args = argparse.Namespace(command="record", file="test.json", speed=1.0)
        mock_parse_args.return_value = mock_args

        # Call the method
        args = self.cli.parse_arguments()

        # Verify result
        assert args.command == "record"
        assert args.file == "test.json"
        assert args.speed == 1.0

    @patch("argparse.ArgumentParser.parse_args")
    def test_parse_arguments_play(self, mock_parse_args):
        """Test parse_arguments method with play command."""
        # Setup mock return value
        mock_args = argparse.Namespace(command="play", file="test.json", speed=2.0)
        mock_parse_args.return_value = mock_args

        # Call the method
        args = self.cli.parse_arguments()

        # Verify result
        assert args.command == "play"
        assert args.file == "test.json"
        assert args.speed == 2.0

    @patch("src.cli.MacroRecorderCLI.parse_arguments")
    @patch("src.cli.MacroRecorderCLI._run_record")
    def test_run_record(self, mock_run_record, mock_parse_args):
        """Test run method with record command."""
        # Setup mock return value
        mock_args = argparse.Namespace(command="record", file="test.json", speed=1.0)
        mock_parse_args.return_value = mock_args

        # Call the method
        self.cli.run()

        # Verify _run_record was called
        mock_run_record.assert_called_once_with("test.json")

    @patch("src.cli.MacroRecorderCLI.parse_arguments")
    @patch("src.cli.MacroRecorderCLI._run_play")
    def test_run_play(self, mock_run_play, mock_parse_args):
        """Test run method with play command."""
        # Setup mock return value
        mock_args = argparse.Namespace(command="play", file="test.json", speed=2.0)
        mock_parse_args.return_value = mock_args

        # Call the method
        self.cli.run()

        # Verify _run_play was called
        mock_run_play.assert_called_once_with("test.json", 2.0)

    @patch("src.cli.MacroRecorderCLI.parse_arguments")
    def test_run_keyboard_interrupt(self, mock_parse_args):
        """Test run method with KeyboardInterrupt."""
        # Setup mock to raise exception
        mock_parse_args.side_effect = KeyboardInterrupt()

        # Call the method (should not raise exception)
        self.cli.run()

    @patch("src.cli.MacroRecorderCLI.parse_arguments")
    def test_run_general_exception(self, mock_parse_args):
        """Test run method with general exception."""
        # Setup mock to raise exception
        mock_parse_args.side_effect = Exception("Test exception")

        # Call the method (should not raise exception)
        self.cli.run()

    @patch("time.sleep", side_effect=KeyboardInterrupt)
    def test_run_record_implementation(self, mock_sleep):
        """Test _run_record implementation."""
        # Call the method (with mocked sleep raising KeyboardInterrupt)
        self.cli._run_record("test.json")

        # Verify recorder was used
        self.mock_recorder_instance.start_recording.assert_called_once()
        self.mock_recorder_instance.stop_recording.assert_called_once()
        self.mock_recorder_instance.save_recording.assert_called_once_with("test.json")

    def test_run_play_implementation(self):
        """Test _run_play implementation."""
        # Call the method
        self.cli._run_play("test.json", 2.0)

        # Verify player was used
        self.mock_player_instance.play.assert_called_once_with("test.json", 2.0)


@patch("src.cli.MacroRecorderCLI")
def test_main(mock_cli):
    """Test main function."""
    # Setup mock
    mock_cli_instance = MagicMock()
    mock_cli.return_value = mock_cli_instance

    # Call the function
    main()

    # Verify CLI was created and run
    mock_cli.assert_called_once()
    mock_cli_instance.run.assert_called_once()
