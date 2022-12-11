"""Helper functions for the ride scheduling script.

This module contains various helper functions that are used by the ride
scheduling script. These functions provide utility functionality such as
converting between different data types, printing text in-place, and
updating nested dictionaries.
"""
import json
import shutil


def stringify_list(l: list[dict]) -> list[str]:
    """Convert a list of dictionaries to strings.

    Args:
        l: The list of dictionaries to convert to strings.

    Returns:
        A list of strings representing the input dictionaries.
    """
    return [json.dumps(o) for o in l]


def dictify_list(l: list[list]) -> list[dict]:
    """Convert a list of JSON-formatted strings to dictionaries.

    Args:
        l: The list of JSON-formatted strings to convert to dictionaries.

    Returns:
        A list of dictionaries representing the input JSON strings.
    """
    return [json.loads(o) for o in l]


def strip_useless_info(rides: list[dict]) -> list[dict]:
    """Strip unnecessary information from a list of ride dictionaries.

    This function takes a list of raw ride dictionaries from the server and
    removes information that is not used in this script in order to save on
    memory usage on the system.

    Args:
        rides: The list of raw ride dictionaries to strip.

    Returns:
        A list of stripped ride dictionaries.
    """
    return [{
        "time": ride["occasions"][0]["time"],
        'location':ride["occasions"][0]["locationName"],
        'cost':ride["occasions"][0]["cost"],
        'date':ride["occasions"][0]["date"],
        'name':ride["occasions"][0]["name"]
    } for ride in rides]


def inplace_print(s: str) -> None:
    """Print a string in-place.

    This function prints a string to the console and overwrites the current
    line of text without adding new lines to the console.

    Args:
        s: The string to print.
    """
    print(s, end="\r", flush=True)


def hide_print(terminal_width: int = None) -> None:
    """Clear the current line on the console.

    This function prints whitespace to the console, overwriting
    the current line of text, and then moves the cursor to the
    beginning of the line. This has the effect of "hiding" the
    current line of text without adding new lines to the console.

    Args:
        terminal_width: The width of the terminal in characters.
            If not provided, the width of the terminal will be
            determined using the shutil module.
    """
    if terminal_width is None:
        (terminal_width, _) = list(shutil.get_terminal_size((80, 20)))

    print(" " * terminal_width, end="\r", flush=True)


def create_requests_proxy(host: str, port: str, protocol: str = 'http') -> dict:
    """Create a proxy configuration for the requests library.

    This function creates a dictionary with proxy configuration
    settings that can be used with the requests library. The
    dictionary contains proxy settings for both HTTP and HTTPS
    requests.

    Args:
        host: The hostname or IP address of the proxy server.
        port: The port number of the proxy server.
        protocol: The protocol to use for the proxy server.
            This should be either "http" or "https". The default
            value is "http".

    Returns:
        A dictionary with proxy configuration settings for the
        requests library.
    """
    return {
        "http": f'{protocol}://{host}:{port}',
        "https": f'{protocol}://{host}:{port}'
    }
