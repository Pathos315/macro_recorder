from src.cli import MacroRecorderCLI


def main() -> None:
    """Main entry point for the macro recorder application."""
    cli = MacroRecorderCLI()
    cli.run()


if __name__ == "__main__":
    main()
