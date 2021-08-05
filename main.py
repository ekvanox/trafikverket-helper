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

COOKIES = {'forarprov-ext':'ffffffff0914194145525d5f4f58455e445a4a423660',
'_pk_id.4.825a':'f363024c09bf6441.1627998880.',
'_pk_ref.4.825a':'%5B%22%22%2C%22%22%2C1627998880%2C%22https%3A%2F%2Fwww.trafikverket.se%2F%22%5D',
'_pk_ses.4.825a':'1',
'ASP.NET_SessionId':'et03qewm20tmfm3l2i4sricm',
'LoginValid':'2021-08-03 16:27',
'FpsExternalIdentity':'D47D328756636AD23417312798AF4DAAA4073268D3710322FDF5143B31B59335719929C80521F1A8EE989AB51D9BC53C4D343F25A0FCDE2AE73BA2C3463CBDFE4A22B3D5A26599C7237010B41301418A38A7FAD2932548EF11B102B04BBD73A6300A1A15FCE90D5B09F60D7493B39E828A5D4CFAEDF873AD038E5A9D0F5B7A2680E8C49699E4BB63E8D739BFAE2F163E11D94761E79815604A3929AAE31FD5F0C9C035D7645D80223314B536DBDD4167EF2440DF0BDA8F600BA20B5653D09BDBC85C50155FF5565C210CF51FC220FEA1E75D27763C9512704F9147919AD56AAA19CDD8362DC33EC09C20CC195E9B8E64B36FB6D08D0AD4BB30F1EF04AA0E557E0F961E4330EE104C09760FCA95AA1C5FCBF43CA8F88B29649CD912A2AF44DF59D60561B28360AC4060FF97121DEF61C107581EC3158A851646B842F3D827A19ED3B75DB2503B3DB3D82065EA8D64DA3A80F604691AA7C9ADE7EB5DC19817AF14241F8F042F2FFE2B242D1F88595E3C7D057FFB832371052D677D5363B6272E226E2A8F94D4B419732CF25DFAFA67784A9C67DBF9B3C54E36DFE4E530D0E01715F131586BBBF3CDCD261D1CF3406E62BA'}
USERAGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
SLEEP_TIME = 60

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

# Predefined location ids to search
valid_location_ids = [1000001,1000003,1000004,1000005,1000006,1000007,1000008,1000009,1000010,1000011,1000012,1000015,1000019,1000020,1000021,1000022,1000027,1000028,1000029,1000030,1000031,1000035,1000036,1000037,1000038,1000039,1000040,1000041,1000044,1000045,1000046,1000047,1000048,1000053,1000055,1000056,1000057,1000059,1000060,1000061,1000062,1000063,1000064,1000065,1000066,1000067,1000068,1000069,1000070,1000071,1000072,1000074,1000075,1000076,1000077,1000078,1000082,1000083,1000084,1000085,1000086,1000087,1000088,1000089,1000090,1000091,1000092,1000093,1000094,1000095,1000096,1000097,1000098,1000099,1000100,1000101,1000102,1000103,1000104,1000105,1000106,1000107,1000108,1000109,1000111,1000112,1000114,1000115,1000116,1000118,1000119,1000120,1000121,1000122,1000123,1000124,1000126,1000127,1000129,1000130,1000132,1000134,1000135,1000137,1000139,1000143,1000145,1000149,1000317,1000318,1000321,1000322,1000325,1000326,1000327,1000328,1000329,1000330]

# Load class into object
trafikverket_api = TrafikverketAPI(cookies=COOKIES, useragent=USERAGENT, proxy=PROXY, SSN='20020214-1891', examination_type_id=EXAMINATION_DICT[EXAMINATION_TYPE])

old_stringified_list = set([])

while 1:
    # Reset variables
    available_rides_list = []

    # Sync local ride info with server
    for location_id in tqdm(valid_location_ids,desc='Updating available locations', unit='id', leave=False):
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

    # See if available rides have changed since previous sync
    helpers.inplace_print(f'Database size: {len(available_rides_list)} | Last check: {int(time()-last_check_time)}s ago')
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
    for i in range(SLEEP_TIME, 0, -1):
        helpers.inplace_print(f'Database size: {len(available_rides_list)} | Next sync in: {i}s ')
        sleep(1)
    helpers.hide_print()