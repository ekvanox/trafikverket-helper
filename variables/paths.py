# Import the Path class from the pathlib module
from pathlib import Path

working_directory = Path.cwd()
project_directory = Path(__file__).parent.parent

# Create Path objects representing the file paths
config_file = working_directory / 'config.json'
