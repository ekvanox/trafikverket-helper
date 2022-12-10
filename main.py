import json
from time import sleep, time

import questionary
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm

import constants
from api import TrafikverketAPI
from helpers import helpers, io, output

# Disable insecure request warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger = output.create_logger(logging_dir='log')


# User selection
EXAMINATION_TYPE: str = questionary.select(
    'Select exam type:', choices=["Kunskapsprov", "Körprov"]).ask()
EXECUTION_MODE: str = questionary.select(
    'Select execution mode:', choices=["Sort by date", "Log server changes", "Start web server"]).ask()

CONFIG = io.load_config()

if 'proxy' in CONFIG:
    proxy_config = CONFIG['proxy']
    proxy = helpers.create_requests_proxy(
        host=proxy_config['host'],
        port=proxy_config['port'],
        protocol=proxy_config.get('protocol', 'http'),
    )
else:
    proxy: str = questionary.select(
        'Select request proxy:', choices=["None", "Fiddler", "TOR"]).ask()

    # Set proxy for requests library
    proxy = constants.proxy_select[proxy]

# Load class into object
trafikverket_api = TrafikverketAPI(
    cookies=constants.cookies,
    useragent=constants.useragent,
    proxy=proxy,
    ssn=CONFIG['swedish_ssn'],
    examination_type_id=constants.examination_dict[EXAMINATION_TYPE],
)

# Select execution mode
if EXECUTION_MODE == "Sort by date":
    # Reset variables
    available_rides_list = []

    # Sync local ride info with server
    for location_id in tqdm(
        constants.valid_location_ids[EXAMINATION_TYPE],
        desc='Updating local database',
        unit='id',
        leave=False,
    ):
        # Set the maximum number of attempts to retrieve the available rides
        MAX_ATTEMPTS = 10
        WAIT_TIME = 2

        # Try to retrieve the available rides up to the maximum number of attempts
        for attempt in range(MAX_ATTEMPTS):
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
            except Exception as e:
                logger.exception(
                    'Unfixable error occurred with location id: %s\n%s', location_id, e
                )
                # Wait for the specified time before retrying
                sleep(WAIT_TIME)

    # Sort by date
    for ride in sorted(available_rides_list, key=lambda x: (x['date'], x['time']), reverse=True):
        logger.info(
            f'{ride["name"]}, {ride["date"]} {ride["time"]} in {ride["location"]} for {ride["cost"]}'
        )

    logger.info(
        f'Total: {len(available_rides_list)}'
    )

elif EXECUTION_MODE == "Log server changes":
    old_stringified_list = set([])

    while 1:
        try:
            POLLING_FREQUENCY: int = int(questionary.text(
                'Enter polling frequency:', default="60").ask())
            break
        except Exception as e:
            logger.exception(f'Invalid input {e}')

    while 1:
        # Reset variables
        available_rides_list = []

        # Sync local ride info with server
        for location_id in tqdm(constants.valid_location_ids[EXAMINATION_TYPE], desc='Updating local database', unit='id', leave=False):
            for _ in range(10):
                try:
                    available_rides_list.extend(helpers.strip_useless_info(
                        trafikverket_api.get_available_dates(
                            location_id,
                            extended_information=True,
                        )
                    ))
                    break
                except Exception as e:
                    logger.error(
                        f'Unfixable error occurred with location id: {location_id}\n{e}'
                    )
                sleep(2)

        # Update last check time
        last_check_time = time()

        # Next available date
        next_available_ride = sorted(
            available_rides_list, key=lambda x: (x['date'], x['time']))[0]

        # See if available rides have changed since previous sync
        helpers.inplace_print(
            f'Database size: {len(available_rides_list)} | '
            f'Next sync in: {POLLING_FREQUENCY}s | '
            f'Next available: {next_available_ride["date"]} {next_available_ride["time"]} in {next_available_ride["location"]}'
        )

        new_stringified_list = set(
            helpers.stringify_list(available_rides_list)
        )

        added_rides = map(json.dumps, list(
            new_stringified_list-old_stringified_list))
        removed_rides = helpers.dictify_list(
            list(old_stringified_list - new_stringified_list))
        old_stringified_list = new_stringified_list
        helpers.hide_print()

        # Print server client diff
        for ride in added_rides:
            # Example: "[Added] Kunskapsprov B, 2022-01-07 11:15 in Örebro for 325kr"
            if ride["location"] == 'Karlskrona' and "2021-08-" in ride["date"]:
                for i in range(100):
                    print('\a')
                    sleep(1)
            logger.info(
                f'\033[92m[Added] {ride["name"]}, {ride["date"]} {ride["time"]} in {ride["location"]} for {ride["cost"]}\033[0m'
            )
        for ride in removed_rides:
            # Example: "[Removed] Kunskapsprov B, 2022-01-07 11:15 in Örebro for 325kr"
            logger.info(
                f'\033[91m[Removed] {ride["name"]}, {ride["date"]} {ride["time"]} in {ride["location"]} for {ride["cost"]}\033[0m'
            )

        # Sleep between server request sessions
        for i in range(POLLING_FREQUENCY, 0, -1):
            helpers.inplace_print(
                f'Database size: {len(available_rides_list)} | Next sync in: {i}s | Next available: {next_available_ride["date"]} {next_available_ride["time"]} in {next_available_ride["location"]} ')
            sleep(1)
        helpers.hide_print()
else:
    raise NotImplementedError
