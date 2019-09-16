''' Module to handle account related tasks '''
import json
import os

from settings import OUTPUT_DIR

from .exceptions import BadResponseException
from .chest import get_player_loot_map


def login(connection, account):
    ''' Login macro '''
    data = {
        "password": account.password,
        "username": account.username,
    }
    connection.post('/lol-login/v1/session', json=data)
    return {'description': 'Login request sent'}


def get_owned_champions(connection):
    ''' Gets and returns the owned champions data '''
    res = connection.get('/lol-champions/v1/owned-champions-minimal/')
    if res.status_code == 404:
        raise BadResponseException
    res_json = res.json()
    if res_json == []:
        raise BadResponseException
    filtered = list(
        filter(lambda m: m["ownership"]["owned"], res_json))
    return filtered


def get_wallet(connection):
    ''' Gets and returns the wallet data '''
    res = connection.get('/lol-store/v1/wallet/')
    return res.json()


def get_account_details(connection, account):
    ''' Gets and saves accounts data to file '''
    output = {
        'username': account.username,
        'password': account.password,
        'wallet': get_wallet(connection),
        'owned_champions': get_owned_champions(connection),
        'player_loot_map': get_player_loot_map(connection),
    }

    file_name = '{}.json'.format(account.username)
    with open(os.path.join(OUTPUT_DIR, 'accounts', file_name), 'w') as file:
        json.dump(output, file, indent=4,)
