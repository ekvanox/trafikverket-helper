import duallog
import questionary
import requests
import coloredlogs
import logging
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import questionary
from tqdm import tqdm
from time import sleep, time

from api import TrafikverketAPI
import helpers
import constants

# Disable insecure request warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Setup logging
duallog.setup('log')    # Write logs to log directory
logger = logging.getLogger(__name__)

coloredlogs.install(
    level=20,
    fmt="[%(filename)s][%(levelname)s] %(asctime)s: %(message)s",
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


PROXY: str = questionary.select(
    'Select request proxy:', choices=["None", "Fiddler", "TOR"]).ask()

# Set proxy for requests library
PROXY = constants.PROXY_SELECT[PROXY]

EXAMINATION_TYPE: str = questionary.select(
    'Select exam type:', choices=["Kunskapsprov", "Körprov"]).ask()

EXECUTION_MODE: str = questionary.select(
    'Select execution mode:', choices=["Sort by date", "Log server changes", "Start web server"]).ask()


# Load class into object
trafikverket_api = TrafikverketAPI(cookies=constants.COOKIES, useragent=constants.USERAGENT, proxy=PROXY, SSN=constants.SSN, examination_type_id=constants.EXAMINATION_DICT[EXAMINATION_TYPE])

# Select execution mode
if EXECUTION_MODE == "Sort by date":
    # Reset variables
    available_rides_list = []

    # Sync local ride info with server
    for location_id in tqdm(constants.VALID_LOCATION_IDS[EXAMINATION_TYPE] ,desc='Updating local database', unit='id', leave=False):
        for _ in range(10):
            try:
                available_rides_list.extend(helpers.strip_useless_info(trafikverket_api.get_available_dates(location_id, extended_information=True)))
                break
            except Exception as e:
                error = e
                pass
            sleep(2)
        else:
            logger.error(f'Unfixable error occurred with location id: {location_id}\n{error}')

    # Sort by date
    for ride in sorted(available_rides_list, key=lambda x: (x['date'],x['time']), reverse=True):
        logger.info(f'{ride["name"]}, {ride["date"]} {ride["time"]} in {ride["location"]} for {ride["cost"]}')

    logger.info(f'Total: {len(available_rides_list)}')

elif EXECUTION_MODE == "Log server changes":
    old_stringified_list = set([])
    
    while 1:
        try:
            POLLING_FREQUENCY: int = int(questionary.text(
                'Enter polling frequency:',default="60").ask())
            break
        except:
            logger.exception('Invalid input')

    while 1:
        # Reset variables
        available_rides_list = []

        # Sync local ride info with server
        for location_id in tqdm(constants.VALID_LOCATION_IDS[EXAMINATION_TYPE] ,desc='Updating local database', unit='id', leave=False):
            for _ in range(10):
                try:
                    available_rides_list.extend(helpers.strip_useless_info(trafikverket_api.get_available_dates(location_id, extended_information=True)))
                    break
                except Exception as e:
                    error = e
                    pass
                sleep(2)
            else:
                logger.error(f'Unfixable error occurred with location id: {location_id}\n{error}')

        # Update last check time
        last_check_time = time()
        
        # Next available date
        next_available_ride = sorted(available_rides_list, key=lambda x: (x['date'],x['time']))[0]

        # See if available rides have changed since previous sync
        helpers.inplace_print(f'Database size: {len(available_rides_list)} | Next sync in: {POLLING_FREQUENCY}s | Next available: {next_available_ride["date"]} {next_available_ride["time"]} in {next_available_ride["location"]} ')
        new_stringified_list = set(helpers.stringify_list(available_rides_list))
        added_rides = helpers.dictify_list(list(new_stringified_list - old_stringified_list))
        removed_rides = helpers.dictify_list(list(old_stringified_list - new_stringified_list))
        old_stringified_list = new_stringified_list
        helpers.hide_print()

        # Print server client diff
        for ride in added_rides:
            # Example: "[Added] Kunskapsprov B, 2022-01-07 11:15 in Örebro for 325kr"
            logger.info(f'\033[92m[Added] {ride["name"]}, {ride["date"]} {ride["time"]} in {ride["location"]} for {ride["cost"]}\033[0m')
        for ride in removed_rides:
            # Example: "[Removed] Kunskapsprov B, 2022-01-07 11:15 in Örebro for 325kr"
            logger.info(f'\033[91m[Removed] {ride["name"]}, {ride["date"]} {ride["time"]} in {ride["location"]} for {ride["cost"]}\033[0m')

        # Sleep between server request sessions
        for i in range(POLLING_FREQUENCY, 0, -1):
            helpers.inplace_print(f'Database size: {len(available_rides_list)} | Next sync in: {i}s | Next available: {next_available_ride["date"]} {next_available_ride["time"]} in {next_available_ride["location"]} ')
            sleep(1)
        helpers.hide_print()
else:
    raise NotImplementedError