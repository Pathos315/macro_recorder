import argparse
import re
import signal
import sys
from datetime import datetime
from pathlib import Path
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
        """
        Run the record command.

        Args:
            filename: Default path where the recording will be saved
        """
        try:
            self.recorder.start_recording()

            # Wait for keyboard interrupt (Ctrl+C)
            while True:
                sleep(0.1)

        except KeyboardInterrupt:
            self.recorder.stop_recording()

            # Check if any events were recorded
            if not self.recorder.events:
                logger.warning("No events recorded. Nothing to save.")
                return

            # Define macros directory
            macros_dir = Path("macros")
            macros_dir.mkdir(exist_ok=True, parents=True)

            # List existing macros
            existing_macros = list(macros_dir.glob("*.json"))
            if existing_macros:
                logger.info("Existing macros:")
                for macro in existing_macros:
                    logger.info(f"  - {macro.name}")

            # Get default name from original filename or generate one
            original_path = Path(filename)
            default_name = (
                original_path.stem
                if original_path.suffix.lower() == ".json"
                else "macro"
            )

            # Prompt user for macro name
            logger.info(f"Recording complete with {len(self.recorder.events)} events.")

            valid_filename = False
            while not valid_filename:
                print(
                    f"Enter a name for this macro [default: {default_name}]: ",
                    end="",
                    flush=True,
                )
                user_input = input().strip()

                # Use provided name or fallback to default
                macro_name = user_input if user_input else default_name

                # Validate filename (basic check for invalid characters)
                if not re.match(r"^[a-zA-Z0-9_\-. ]+$", macro_name):
                    logger.warning(
                        "Invalid filename. Please use only letters, numbers, spaces, and these characters: _ - ."
                    )
                    continue

                # Ensure .json extension
                if not macro_name.lower().endswith(".json"):
                    macro_name += ".json"

                # Full path for the macro file
                macro_path = macros_dir / macro_name

                # Check if file already exists and prompt for overwrite if needed
                if macro_path.exists():
                    print(
                        f"File {macro_path} already exists. Overwrite? (y/n): ",
                        end="",
                        flush=True,
                    )
                    should_overwrite = input().strip().lower() == "y"
                    if not should_overwrite:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        macro_name = f"{Path(macro_name).stem}_{timestamp}.json"
                        macro_path = macros_dir / macro_name
                        logger.info(f"Using unique name: {macro_path.name}")

                valid_filename = True

            # Save the recording
            self.recorder.save_recording(str(macro_path))
            logger.info(f"Macro saved as: {macro_path}")

    def _run_play(self, filename: str, speed_factor: float) -> None:
        """Run the play command."""
        self.player.play(filename, speed_factor)
