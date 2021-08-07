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

COOKIES = {}
USERAGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'

PROXY: str = questionary.select(
    'Select request proxy:', choices=["None", "Fiddler", "TOR"]).ask()

# Set proxy for requests library
if PROXY == "None":
    PROXY: dict = {
        "http": None,
        "https": None,
    }
elif PROXY == 'Fiddler':
    PROXY = {
        "http": 'http://127.0.0.1:8888',
        "https": 'http://127.0.0.1:8888',
    }
elif PROXY == 'TOR':
    PROXY = {
        "http": 'socks5h://localhost:9050',
        "https": 'socks5h://localhost:9050',
    }

EXAMINATION_DICT = {'Kunskapsprov':3, 'Körprov':12}

EXAMINATION_TYPE: str = questionary.select(
    'Select exam type:', choices=["Kunskapsprov", "Körprov"]).ask()

EXECUTION_MODE: str = questionary.select(
    'Select execution mode:', choices=["Sort by date", "Log server changes", "Start web server"]).ask()

SSN = "20021017-0171"

# Predefined location ids to search
valid_location_ids = {'Körprov': [1000137,1000108,1000109,1000032,1000099,1000083,1000121,1000100,1000066,1000075,1000072,1000005,1000065,1000039,1000060,1000070,1000098,1000019,1000033,1000330,1000006,1000317,1000090,1000118,1000325,1000143,1000059,1000114,1000084,1000101,1000123,1000331,1000056,1000057,1000045,1000091,1000326,1000115,1000074,1000085,1000093,1000048,1000003,1000047,1000031,1000007,1000068,1000092,1000010,1000139,1000046,1000035,1000327,1000321,1000145,1000040,1000124,1000069,1000004,1000009,1000028,1000055,1000102,1000082,1000062,1000022,1000053,1000061,1000103,1000129,1000012,1000104,1000011,1000329,1000135,1000096,1000149,1000020,1000076,1000050,1000094,1000086,1000087,1000049,1000041,1000119,1000044,1000111,1000130,1000107,1000134,1000008,1000054,1000116,1000105,1000036,1000117,1000037,1000120,1000132,1000051,1000077,1000063,1000131,1000126,1000067,1000021,1000071,1000322,1000078,1000027,1000015,1000023,1000097,1000127,1000318,1000095,1000038,1000030,1000064,1000052,1000328,1000029,1000088,1000122,1000001,1000106,1000112,1000073,1000089], 'Kunskapsprov': [1000109,1000032,1000121,1000066,1000005,1000039,1000060,1000098,1000019,1000090,1000118,1000325,1000143,1000059,1000084,1000123,1000056,1000057,1000091,1000326,1000074,1000085,1000093,1000048,1000003,1000047,1000031,1000092,1000046,1000035,1000040,1000124,1000069,1000009,1000028,1000082,1000062,1000022,1000061,1000129,1000011,1000329,1000096,1000149,1000094,1000086,1000087,1000111,1000130,1000107,1000140,1000105,1000036,1000117,1000037,1000132,1000324,1000126,1000021,1000071,1000322,1000078,1000027,1000015,1000097,1000127,1000318,1000095,1000038,1000030,1000064,1000029,1000088,1000122,1000001,1000106,1000112,1000089]}

# Load class into object
trafikverket_api = TrafikverketAPI(cookies=COOKIES, useragent=USERAGENT, proxy=PROXY, SSN=SSN, examination_type_id=EXAMINATION_DICT[EXAMINATION_TYPE])

if EXECUTION_MODE == "Sort by date":
    # Reset variables
    available_rides_list = []

    # Sync local ride info with server
    for location_id in tqdm(valid_location_ids[EXAMINATION_TYPE] ,desc='Updating local database', unit='id', leave=False):
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
        for location_id in tqdm(valid_location_ids[EXAMINATION_TYPE] ,desc='Updating local database', unit='id', leave=False):
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