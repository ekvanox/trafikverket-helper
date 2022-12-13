# Import the Path class from the pathlib module
from pathlib import Path

working_directory = Path.cwd()
project_directory = Path(__file__).parent.parent
logging_directory = working_directory / 'log'

# Create Path objects representing the file paths
config_file = working_directory / 'config.json'
valid_locations_path = project_directory / 'data' / 'valid_locations.json'
