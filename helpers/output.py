import logging
import os
import time

import click
import coloredlogs
import verboselogs


class RemoveColorFilter(logging.Filter):
    """
    A logging filter that removes color codes from log messages.
    """

    def filter(self, record):
        # Check if record is valid and has a message
        if record and record.msg and isinstance(record.msg, str):
            # Remove color codes from log message
            record.msg = click.unstyle(record.msg)

        # Return True to allow the log message to be processed
        return True


def create_logger(name=None, logging_dir=None) -> logging.Logger:
    """
    Create a logger.

    Args:
        name: The name of the logger. Defaults to None.
        logging_dir: The directory to store log files in. Defaults to None.

    Returns:
        A logger instance.
    """

    # Initialize verbose logger
    logger = verboselogs.VerboseLogger(name)

    # Add file handler to logger
    log_file = os.path.join(logging_dir, f"{int(time.time())}.log")
    file_handler = logging.FileHandler(log_file)
    logger.addHandler(file_handler)

    # Set log level for file handler
    file_handler.setLevel(logging.DEBUG)

    # Format log messages to include date and time
    if name:
        fmt = f"[%(levelname)s][{name}] %(asctime)s: %(message)s"
    else:
        fmt = "[%(levelname)s] %(asctime)s: %(message)s"

    # Create formatter and set it for the file handler
    formatter = logging.Formatter(fmt)
    file_handler.setFormatter(formatter)

    # Filter out all colors from the output
    color_filter = RemoveColorFilter()
    file_handler.addFilter(color_filter)

    # Setup logging
    coloredlogs.install(
        level=20,
        fmt=fmt,
        level_styles={
            "critical": {"bold": True, "color": "red"},
            "debug": {"color": "green"},
            "error": {"color": "red"},
            "info": {"color": "white"},
            "notice": {"color": "magenta"},
            "spam": {"color": "green", "faint": True},
            "success": {"bold": True, "color": "green"},
            "verbose": {"color": "blue"},
            "warning": {"color": "yellow"},
        },
        logger=logger,
        field_styles={
            "asctime": {"color": "cyan"},
            "levelname": {"bold": True, "color": "black"},
        },
        isatty=True,
    )

    return logger
