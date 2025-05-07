# Macro Recorder

A clean, object-oriented Python application for recording and replaying mouse and keyboard actions with precision.

## Overview

Macro Recorder allows you to record sequences of mouse movements, clicks, and keyboard inputs, then play them back exactly as recorded. This tool is perfect for automating repetitive tasks, testing UI interactions, or creating demonstrations.

## Features

- Record mouse movements, clicks, and keyboard actions
- Playback recorded macros at adjustable speeds
- Smart throttling to reduce unnecessary mouse movement events
- Double-click detection
- Visual countdown before recording/playback starts
- Clean JSON-based storage format
- Cross-platform support (Windows, macOS, Linux)

## Installation

### Prerequisites

- Python 3.6+
- Required Python packages:
  - pynput
  - pyautogui
  - keyboard
  - mouse
  - tkinter (usually comes with Python)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/macro-recorder.git
   cd macro-recorder
   ```

2. Install dependencies:
   ```bash
   pip install pynput pyautogui keyboard mouse
   ```

## Usage

### Recording a Macro

To record mouse and keyboard actions:

```bash
python cli.py record --file macros/my_macro.json
```

A countdown will appear, then recording will begin. Press Ctrl+C to stop recording.

### Playing a Macro

To play back a recorded macro:

```bash
python cli.py play --file macros/my_macro.json --speed 1.0
```

The `--speed` parameter accepts values like 0.5 (half speed), 1.0 (normal speed), or 2.0 (double speed).

## Architecture

The application follows a clean, modular architecture with separation of concerns:

- **CLI Layer**: Command-line interface for user interaction
- **Core Layer**: Main business logic for recording and playback
- **Model Layer**: Domain models representing the data
- **I/O Layer**: Adapters for mouse/keyboard input and output
- **Storage Layer**: Persistence of macro recordings

### Key Components

- `MacroRecorder`: Records mouse and keyboard events
- `MacroPlayer`: Replays recorded macros with timing fidelity
- `CountdownUI`: Displays a visual countdown before actions
- `InputAdapter`/`OutputAdapter`: Abstract interfaces for I/O operations
- `MacroStorage`: Handles saving and loading macro files

## Configuration Options

You can adjust various settings in the `Configuration` class:

- Screen dimensions
- Mouse movement throttling parameters
- Double-click detection thresholds
- Countdown settings
- Replay delay

## File Format

Macro recordings are stored as JSON files containing a sequence of actions with timestamps and positions. The time differences between actions are preserved during playback to maintain timing fidelity.

## Limitations

- The application requires appropriate permissions to control mouse and keyboard
- Some applications with advanced security features may block simulated inputs
- Recordings are resolution-dependent, so playback works best at the same screen resolution as recording

## License

[Insert your license information here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements

This project uses several open-source libraries:
- pynput for monitoring input events
- pyautogui for cursor control
- keyboard for keyboard control