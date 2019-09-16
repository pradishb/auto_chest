''' Module to handle chests related tasks '''
import json
import os
import time

from settings import OUTPUT_DIR

from .exceptions import LootRetrieveException


def get_loot(connection):
    ''' Get loot data from the server '''
    res = connection.get('/lol-loot/v1/player-loot/')
    res_json = res.json()
    if res_json == []:
        raise LootRetrieveException
    return res_json


def get_player_loot_map(connection):
    ''' Get player loot map from the server '''
    res = connection.get('/lol-loot/v1/player-loot-map/')
    return res.json()


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
    connection.post(
        '/lol-loot/v1/recipes/MATERIAL_key_fragment_forge/craft?repeat={}'.format(
            repeat), json=['MATERIAL_key_fragment'])


def open_generic_chests(connection, account, repeat=1):
    ''' Opens a chest and saves it data to json '''
    if repeat == 0:
        return
    res = connection.post(
        '/lol-loot/v1/recipes/CHEST_generic_OPEN/craft?repeat={}'.format(
            repeat), json=['CHEST_generic', 'MATERIAL_key'])

    file_name = '{}_{}.json'.format(account.username, time.time())
    with open(os.path.join(OUTPUT_DIR, 'chests', file_name), 'w') as file:
        json.dump(res.json(), file, indent=4,)
