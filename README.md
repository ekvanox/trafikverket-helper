# Trafikverket API

[![Version](https://img.shields.io/github/v/release/ekvanox/trafikverket-helper)](https://img.shields.io/github/v/release/ekvanox/trafikverket-helper)
![GitHub repo size](https://img.shields.io/github/repo-size/ekvanox/trafikverket-helper)
[![CodeFactor](https://www.codefactor.io/repository/github/ekvanox/trafikverket-helper/badge)](https://www.codefactor.io/repository/github/ekvanox/trafikverket-helper)
![License](https://img.shields.io/github/license/ekvanox/trafikverket-helper)

This is a script for interacting with the Trafikverket API to retrieve information about available rides for driving examinations. It allows the user to select an examination type and execution mode, then retrieves available rides from the API and displays them in the console.

![Usage example gif](https://github.com/ekvanox/trafikverket-helper/blob/master/images/usage.gif?raw=true)

## Requirements

- Python 3.7 or higher

## Installation

Clone the repository and install the required packages:

```sh
$ git clone https://github.com/ekvanox/trafikverket-helper
$ cd trafikverket-helper
$ pip install -r requirements.txt
```

## Usage

To run the script, use the following command:

```sh
$ python main.py
```

## Modes

The script has three execution modes:

- **Sort by date**: Retrieves the available rides from the API and sorts them by date and time, from earliest to latest.
- **Log server changes**: Retrieves the available rides from the API and continuously logs any changes to the server data, such as new or removed rides.
- **Start web server**: Starts a local web server to display the available rides in a web page.

## Configuration

The script uses a `config.json` file for settings and authentication. The file should be located in the same directory as the script, and should have the following format:

```json
{
  "swedish_ssn": "0123456-7890",
  "proxy": {
    "host": "localhost",
    "port": 8888,
    "protocol": "http"
  }
}
```

The swedish_ssn field should be replaced with a valid Swedish social security number, and the proxy field can be omitted or modified to use a proxy server for the API requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.