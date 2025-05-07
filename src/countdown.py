import time
import tkinter as tk
from tkinter import Canvas, Label

from src.config import Configuration, logger


class CountdownUI:
    """Handles the countdown UI before recording/replaying."""

    def __init__(self, config: Configuration):
        """Initialize with configuration."""
        self.config = config

    def show_countdown(self, mode: str) -> None:
        """
        Display a countdown before starting recording or replay.

        Args:
            mode: Either "record" or "replay"
        """
        logger.info(
            f"{mode.capitalize()} will start in \
            {self.config.countdown_duration} seconds..."
        )

        root = tk.Tk()
        root.attributes("-transparentcolor", self.config.countdown_background)
        root.overrideredirect(1)  # Removes window borders
        root.geometry(f"{self.config.screen_width}x{self.config.screen_height}+0+0")
        root.attributes("-topmost", 1)

        canvas = Canvas(
            root,
            width=self.config.screen_width,
            height=self.config.screen_height,
            bg=self.config.countdown_background,
            highlightthickness=0,
        )
        canvas.pack()

        countdown_label = Label(
            canvas,
            text="",
            font=(self.config.countdown_font, self.config.countdown_font_size),
        )
        countdown_label.place(relx=0.5, rely=0.5, anchor="center")

        # Show countdown
        for i in range(self.config.countdown_duration, 0, -1):
            countdown_label.config(text=str(i))
            root.update()
            time.sleep(1)

        # Show start message
        if mode == "record":
            countdown_label.config(text="Recording has started")
        elif mode == "replay":
            countdown_label.config(text="Replay has started")

        root.update()
        time.sleep(1)

        root.destroy()  # Properly destroy the window when done
