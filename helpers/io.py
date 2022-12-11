"""
A module for safely reading and writing files, including handling exceptions and
creating backup files.

The module provides the following functions:
- safe_write: Write data to a file, creating a backup and handling exceptions.
- safe_json_load: Load a JSON file, returning a default value if the file is not found.
- safe_read: Read a file, returning an empty string if the file is not found.
- load_config: Load the configuration from a JSON file.
- update_config: Update the configuration in the JSON file.
"""


import json
import shutil
from pathlib import Path
from typing import Any

from variables import paths


def safe_write(data: str, file_path: str, backup_path: str = None, create_folders: bool = True, encoding: str = 'utf-8', mode: str = 'w+') -> None:
    """Write data to a file, creating a backup and handling exceptions.

    Args:
        data: The data to write to the file.
        file_path: The path of the file to write to.
        backup_path: The path of the backup file. If not provided, a default
            backup path will be used.
        create_folders: If True, any missing folders in the file path will be
            created. If False, a FileNotFoundError will be raised if any of
            the folders in the file path do not exist.
        encoding: The encoding to use when writing the file.
        mode: The mode to open the file in.

    Raises:
        FileNotFoundError: If the file path or backup path do not exist and
            `create_folders` is False.
    """

    # If no backup path is provided, create a default backup path
    if backup_path is None:
        backup_path = file_path + '.bak'

    # Try writing the data to the backup file
    try:
        with open(backup_path, mode, encoding=encoding) as f:
            f.write(data)
    except FileNotFoundError as e:
        # If the folders in the file path do not exist and create_folders is
        # False, raise the exception
        if not create_folders:
            raise e

        # Create the folder structure for the backup file
        Path(backup_path).mkdir(parents=True, exist_ok=True)

        # Retry writing the data to the backup file
        with open(backup_path, mode, encoding=encoding) as f:
            f.write(data)

    # Move the backup file to the original file path
    shutil.move(backup_path, file_path)


def safe_json_load(file_path: str, default_value: Any, encoding: str = 'utf-8') -> Any:
    """Load a JSON file, returning a default value if the file is not found.

    Args:
        file_path: The path of the file to load.
        default_value: The default value to return if the file is not found.
        encoding: The encoding of the file.

    Returns:
        The contents of the file, or the default value if the file is not found.
    """
    # Try reading the JSON file
    try:
        with open(file_path, 'r+', encoding=encoding) as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        # If the file is not found, create it and write the default value to it
        with open(file_path, 'w', encoding=encoding) as f:
            json.dump(default_value, f)

        # Return the default value
        return default_value


def safe_read(file_path: str, encoding: str = 'utf-8') -> str:
    """Read a file, returning an empty string if the file is not found.

    Args:
        file_path: The path of the file to read.
        encoding: The encoding of the file.

    Returns:
        The contents of the file, or an empty string if the file is not found.
    """
    # Try reading the file
    try:
        with open(file_path, 'r+', encoding=encoding) as f:
            return f.read()
    except FileNotFoundError:
        # If the file is not found, create the folder structure for the file
        Path(file_path).mkdir(parents=True, exist_ok=True)

        # Return an empty string if the file is not found.
        return ''


def load_config() -> dict:
    """Load the configuration from a JSON file.

    Returns:
        A dictionary containing the configuration data.
    """
    return safe_json_load(paths.config_file, default_value={})


def update_config(data: dict) -> None:
    """Update the configuration with the given data.

    Args:
        data: A dictionary containing the data to update the configuration with.
    """
    # Load the current configuration
    config = load_config()

    # Update the configuration with the given data
    config.update(data)

    # Convert the updated configuration to a JSON string
    data = json.dumps(config, indent=4)

    # Write the updated configuration to the file
    safe_write(data, paths.config_file)


def load_location_ids() -> dict:
    return safe_json_load(paths.valid_locations_path, default_value={})
