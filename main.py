from api import TrafikverketAPI
import questionary
import requests
import coloredlogs
import logging
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import questionary
from tqdm import tqdm

# Disable insecure request warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger()
logger.disabled = True
logger = logging.getLogger(__name__)

# Setup logging
coloredlogs.install(
    level=20,
    fmt="[%(levelname)s] %(asctime)s: %(message)s",
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
)

COOKIES = {'forarprov-ext':'ffffffff0914194145525d5f4f58455e445a4a423660',
'_pk_id.4.825a':'f363024c09bf6441.1627998880.',
'_pk_ref.4.825a':'%5B%22%22%2C%22%22%2C1627998880%2C%22https%3A%2F%2Fwww.trafikverket.se%2F%22%5D',
'_pk_ses.4.825a':'1',
'ASP.NET_SessionId':'et03qewm20tmfm3l2i4sricm',
'LoginValid':'2021-08-03 16:27',
'FpsExternalIdentity':'D47D328756636AD23417312798AF4DAAA4073268D3710322FDF5143B31B59335719929C80521F1A8EE989AB51D9BC53C4D343F25A0FCDE2AE73BA2C3463CBDFE4A22B3D5A26599C7237010B41301418A38A7FAD2932548EF11B102B04BBD73A6300A1A15FCE90D5B09F60D7493B39E828A5D4CFAEDF873AD038E5A9D0F5B7A2680E8C49699E4BB63E8D739BFAE2F163E11D94761E79815604A3929AAE31FD5F0C9C035D7645D80223314B536DBDD4167EF2440DF0BDA8F600BA20B5653D09BDBC85C50155FF5565C210CF51FC220FEA1E75D27763C9512704F9147919AD56AAA19CDD8362DC33EC09C20CC195E9B8E64B36FB6D08D0AD4BB30F1EF04AA0E557E0F961E4330EE104C09760FCA95AA1C5FCBF43CA8F88B29649CD912A2AF44DF59D60561B28360AC4060FF97121DEF61C107581EC3158A851646B842F3D827A19ED3B75DB2503B3DB3D82065EA8D64DA3A80F604691AA7C9ADE7EB5DC19817AF14241F8F042F2FFE2B242D1F88595E3C7D057FFB832371052D677D5363B6272E226E2A8F94D4B419732CF25DFAFA67784A9C67DBF9B3C54E36DFE4E530D0E01715F131586BBBF3CDCD261D1CF3406E62BA'}
USERAGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'

PROXY: str = questionary.select(
    'Select request proxy: ', choices=["None", "Fiddler", "TOR"]).ask()

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

# Load class into object
trafikverket_api = TrafikverketAPI(cookies=COOKIES, useragent=USERAGENT, proxy=PROXY, SSN='20020214-1891')

available_rides_list = []

# Get server response
for i in tqdm(range(1000000,1000200)):
    try:
        available_rides_list.extend(trafikverket_api.get_available_dates(i, extended_information=True))
    except:
        logger.error(f'Error on location ID: {i}')

print(available_rides_list)