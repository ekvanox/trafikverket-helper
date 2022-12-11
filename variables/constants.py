MAX_ATTEMPTS = 10
WAIT_TIME = 2

examination_dict = {
    'Kunskapsprov': 3,
    'Körprov': 12
}

proxy_select = {
    'None':
    {
        "http": None,
        "https": None
    },
    'Fiddler': {
        "http": 'http://127.0.0.1:8888',
        "https": 'http://127.0.0.1:8888'
    },
    'TOR': {
        "http": 'socks5h://localhost:9050',
        "https": 'socks5h://localhost:9050'
    }
}

cookies = {}
