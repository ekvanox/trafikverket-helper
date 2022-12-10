import coloredlogs
import duallog
import logging
import questionary
import verboselogs


def create_logger(name=None, logging_dir=None) -> logging.Logger:
    """
    Create a logger.

    Args:
        name: The name of the logger. Defaults to None.
        logging_dir: The directory to store log files in. Defaults to None.

    Returns:
        A logger instance.
    """

    if logging_dir:
        duallog.setup(logging_dir)

    logger = verboselogs.VerboseLogger(name)

    if name:
        fmt = f"[%(levelname)s][{name}] %(asctime)s: %(message)s"
    else:
        fmt = "[%(levelname)s] %(asctime)s: %(message)s"

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
