import time

import questionary
import requests
import urllib3
from termcolor import colored
from tqdm import tqdm
from user_agent import generate_user_agent

from api.exceptions import HTTPStatus
from api.trafikverket import TrafikverketAPI
from helpers import helpers, io, output
from variables import constants

# Disable warnings for unverified HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create the logger and save them in the log directory
logger = output.create_logger(logging_dir='log')

# Ask user to select exam type from a list of choices
EXAMINATION_TYPE: str = questionary.select(
    'Select exam type:', choices=["Kunskapsprov", "Körprov"]).ask()

# Ask user to select execution mode from a list of choices
EXECUTION_MODE: str = questionary.select(
    'Select execution mode:', choices=["Sort by date", "Log server changes", "Start web server"]).ask()

# Load configuration
CONFIG = io.load_config()

# If proxy is defined in the configuration
if 'proxy' in CONFIG:
    # Retrieve proxy configuration
    proxy_config = CONFIG['proxy']
    # Format proxy for requests library
    proxy = helpers.create_requests_proxy(
        host=proxy_config['host'],
        port=proxy_config['port'],
        protocol=proxy_config.get('protocol', 'http'),
    )
else:
    # Ask user to select request proxy from a list of choices
    proxy: str = questionary.select(
        'Select request proxy:', choices=["None", "Fiddler", "TOR"]).ask()

    # Set proxy for requests library
    proxy = constants.proxy_select[proxy]

# Generate a random user agent
useragent = generate_user_agent()

# Load valid location ids
valid_location_ids = io.load_location_ids()

# Load class into object
trafikverket_api = TrafikverketAPI(
    cookies=constants.cookies,
    useragent=useragent,
    proxy=proxy,
    ssn=CONFIG['swedish_ssn'],
    examination_type_id=constants.examination_dict[EXAMINATION_TYPE],
)

# Select execution mode
if EXECUTION_MODE == "Sort by date":
    # Reset the list of available rides
    available_rides_list = []

    # Loop through all valid location IDs for the selected examination type
    for location_id in tqdm(
        valid_location_ids[EXAMINATION_TYPE],
        desc='Updating local database',
        unit='id',
        leave=False,
    ):

        # Try to retrieve the available rides up to the maximum number of attempts
        for attempt in range(constants.MAX_ATTEMPTS):
            try:
                # Get the available rides from the API
                available_rides = helpers.strip_useless_info(
                    trafikverket_api.get_available_dates(
                        location_id,
                        extended_information=True,
                    )
                )

                # Add the available rides to the list
                available_rides_list.extend(available_rides)

                # Stop trying if the available rides were successfully retrieved
                break
            except (HTTPStatus, requests.exceptions.RequestException) as e:
                logger.error(
                    'Unfixable error occurred with location id: %s\n%s', location_id, e
                )
                # Wait for the specified time before retrying
                time.sleep(constants.WAIT_TIME)

    # Sort the avaliable rides based on the date and time
    available_rides_list.sort(
        key=lambda x: (x['date'], x['time']),
        reverse=True
    )

    # Display all the available rides
    for ride in available_rides_list:
        logger.info(
            '%s, %s %s in %s for %s',
            ride["name"],
            ride["date"],
            ride["time"],
            ride["location"],
            ride["cost"]
        )

    # Show the total amount of rides found
    logger.info(
        'Total: %s', len(available_rides_list)
    )

elif EXECUTION_MODE == "Log server changes":
    # Set of ride information dictionaries
    last_available_rides = set([])

    while 1:
        # Ask user to input polling frequency
        try:
            POLLING_FREQUENCY = int(questionary.text(
                'Enter polling frequency:', default='300').ask())
            break
        except ValueError as e:
            # Log input error
            logger.exception('Invalid input: %s', e)

    while 1:
        # List to store ride information dictionaries
        available_rides_list = []

        # Retrieve list of valid location IDs for the examination type
        for location_id in tqdm(
            valid_location_ids[EXAMINATION_TYPE],
            desc='Updating local database',
            unit='id',
            leave=False
        ):
            for _ in range(constants.MAX_ATTEMPTS):
                try:
                    # Retrieve available dates from server and add to list, stripping unnecessary information
                    available_rides_list.extend(helpers.strip_useless_info(
                        trafikverket_api.get_available_dates(
                            location_id,
                            extended_information=True,
                        )
                    ))
                    break
                except (HTTPStatus, requests.exceptions.RequestException) as e:
                    # Log error
                    logger.error(
                        'Unfixable error occurred with location id: %s\n%s', location_id, e
                    )
                # Sleep for specified time before trying again
                time.sleep(constants.WAIT_TIME)

        # Update last check time
        last_check_time = time.time()

        # Sort the list of ride information dictionaries by date and time
        next_available_ride = sorted(
            available_rides_list,
            key=lambda x: (x['date'], x['time'])
        )[0]

        # Print current information to console
        helpers.inplace_print(
            f'Database size: {len(available_rides_list)} | '
            f'Next sync in: {POLLING_FREQUENCY}s | '
            f'Next available: {next_available_ride["date"]} {next_available_ride["time"]} in {next_available_ride["location"]}'
        )

        # Convert the list of dictionaries into a set
        available_rides = {tuple(d.items()) for d in available_rides_list}

        # Find the difference between available rides and last available rides
        added_rides = available_rides.difference(last_available_rides)
        # Convert tuples back to dictionaries
        added_rides = (dict(v) for v in added_rides)

        # Find the difference between last available rides and available rides
        removed_rides = last_available_rides.difference(available_rides)
        # Convert tuples back to dictionaries
        removed_rides = (dict(v) for v in removed_rides)

        # Update last available rides
        last_available_rides = available_rides
        # Hide the in-place print output
        helpers.hide_print()

        # Print added rides to console
        for ride in added_rides:
            # Example: "[Added] Kunskapsprov B, 2022-01-07 11:15 in Örebro for 325kr"
            logger.info(
                colored(
                    f'[Added] {ride["name"]}, {ride["date"]} {ride["time"]} in {ride["location"]} for {ride["cost"]}',
                    'green'
                )
            )

        for ride in removed_rides:
            # Example: "[Removed] Kunskapsprov B, 2022-01-07 11:15 in Örebro for 325kr"
            logger.info(
                colored(
                    f'[Removed] {ride["name"]}, {ride["date"]} {ride["time"]} in {ride["location"]} for {ride["cost"]}',
                    'red'
                )
            )

        # Update countdown timer until next update
        for i in range(POLLING_FREQUENCY, 0, -1):
            helpers.inplace_print(
                f'Database size: {len(available_rides_list)} | '
                f'Next sync in: {i}s | '
                f'Next available: {next_available_ride["date"]} {next_available_ride["time"]} in {next_available_ride["location"]}'
            )
            time.sleep(1)

        # Hide the in-place print output
        helpers.hide_print()
else:
    raise NotImplementedError
