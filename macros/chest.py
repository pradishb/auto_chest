''' Module to handle chests related tasks '''
import json
import os
import time

import requests

from settings import OUTPUT_DIR

from .exceptions import CompletedAccount


class LootRetrieveException(Exception):
    ''' Raised when there is an error retriving loot '''


def get_loot(connection):
    ''' Get loot data from the server '''
    res = requests.get(
        connection.url + '/lol-loot/v1/player-loot/', **connection.kwargs)
    res_json = res.json()
    if res_json == []:
        raise LootRetrieveException
    return res_json


def get_key_fragment_count(loot_json):
    ''' Returns the key fragment count '''
    key_fragment = list(
        filter(lambda l: l['lootId'] == 'MATERIAL_key_fragment', loot_json))
    if key_fragment == []:
        return 0
    return key_fragment[0]['count']


def get_key_count(loot_json):
    ''' Returns the key count '''
    key = list(
        filter(lambda l: l['lootId'] == 'MATERIAL_key', loot_json))
    if key == []:
        return 0
    return key[0]['count']


def get_generic_chest_count(loot_json):
    ''' Returns the generic chest count '''
    generic_chest = list(
        filter(lambda l: l['lootId'] == 'CHEST_generic', loot_json))
    if generic_chest == []:
        return 0
    return generic_chest[0]['count']


def forge(connection, repeat=1):
    ''' Forges key fragment to keys '''
    if repeat == 0:
        return
    url = "https://{}/lol-loot/v1/recipes/MATERIAL_key_fragment_forge/craft?repeat={}".format(
        connection["url"], repeat)
    requests.post(
        url, verify=False, auth=('riot', connection["authorization"]), timeout=30,
        json=['MATERIAL_key_fragment']
    )


def open_generic_chests(connection, account, repeat=1):
    ''' Opens a chest and saves it data to json '''
    if repeat == 0:
        return
    url = "https://%s/lol-loot/v1/recipes/CHEST_generic_OPEN/craft?repeat=%d" % (
        connection["url"], repeat)
    res = requests.post(
        url, verify=False, auth=('riot', connection["authorization"]), timeout=30,
        json=['CHEST_generic', 'MATERIAL_key'])
    file_name = '{}_{}.json'.format(account.username, time.time())
    with open(os.path.join(OUTPUT_DIR, file_name), 'w') as file:
        json.dump(res.json(), file)


def open_chests(connection, account):
    ''' Main function of the script '''
    loot_json = get_loot(connection)
    forgable_keys = get_key_fragment_count(loot_json)//3
    if forgable_keys > 0:
        forge(connection, forgable_keys)
        return {'description': 'Forging {} keys'.format(forgable_keys)}
    generic_chest_count = get_generic_chest_count(loot_json)
    key_count = get_key_count(loot_json)
    if min(key_count, generic_chest_count) > 0:
        open_generic_chests(connection, account)
        return {
            'generic_chest_count': generic_chest_count,
            'key_count': key_count,
            'description': 'Opening a chest'
        }
    raise CompletedAccount
