import argparse
import signal
import sys
from time import sleep
from types import FrameType

import keyboard as keyboard_hooks  # type: ignore

from src.config import Configuration, logger
from src.core import MacroPlayer, MacroRecorder


class MacroRecorderCLI:
    """Command-line interface for the macro recorder."""

    def __init__(self) -> None:
        """Initialize the CLI."""
        self.config = Configuration()
        self.recorder = MacroRecorder(self.config)
        self.player = MacroPlayer(self.config)

        # Set up signal handler for clean exits
        signal.signal(signal.SIGINT, self.signal_handler)  # type: ignore

    def signal_handler(
        self,
        sig: int,
        frame: FrameType | None,
    ) -> None:
        """
        Handle interruption signals like Ctrl+C.
        Ensures clean exit with proper cleanup.

        Args:
            sig: Signal number
            frame: Current stack frame or None
        """
        logger.info("\nInterrupted, cleaning up...")
        self.cleanup_keyboard_state()

        # If recording was in progress, make sure to stop it properly
        if hasattr(self, "recorder") and self.recorder:
            try:
                self.recorder.stop_recording()
                # Could optionally still save the recording here with:
                # self.recorder.save_recording("last_interrupted_recording.json")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")

        sys.exit(0)

    def cleanup_keyboard_state(self) -> None:
        """
        Reset all potentially pressed keys to ensure none remain 'stuck'.
        This function should be called when the program exits normally or due to an error.
        """
        logger.info("Cleaning up keyboard state...")

        # Common keys that might get stuck
        keyboard_hooks.release("ctrl")
        keyboard_hooks.unhook_all()

    def parse_arguments(self) -> argparse.Namespace:
        """Parse command-line arguments."""
        parser = argparse.ArgumentParser(
            description="Mouse and Keyboard Macro Recorder/Player"
        )
        parser.add_argument(
            "command", choices=["record", "play"], help="Choose command: record or play"
        )
        parser.add_argument(
            "--file",
            default="macros/macro_actions.json",
            help="File to save/load macro actions (default: macros/macro_actions.json)",
        )
        parser.add_argument(
            "--speed",
            type=float,
            default=1.0,
            help="Speed factor for playback (default: 1.0)",
        )

        return parser.parse_args()

    def run(self) -> None:
        """Run the CLI application."""
        args = self.parse_arguments()

        try:
            if args.command == "record":
                self._run_record(args.file)
            elif args.command == "play":
                self._run_play(args.file, args.speed)
        except KeyboardInterrupt:
            logger.info("Application terminated by user.")
        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
        finally:
            self.cleanup_keyboard_state()

    def _run_record(self, filename: str) -> None:
        """Run the record command."""
        try:
            self.recorder.start_recording()

            # Wait for keyboard interrupt (Ctrl+C)
            while True:
                sleep(0.1)

        except KeyboardInterrupt:
            self.recorder.stop_recording()
            self.recorder.save_recording(filename)

    def _run_play(self, filename: str, speed_factor: float) -> None:
        """Run the play command."""
        self.player.play(filename, speed_factor)


# =====================================
# Application Entry Point
# =====================================


def main() -> None:
    """Main entry point for the macro recorder application."""
    cli = MacroRecorderCLI()
    cli.run()


if __name__ == "__main__":
    main()
