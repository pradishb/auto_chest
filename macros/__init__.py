''' Module to do macro tasks '''
import requests

from process import open_league_client, restart_league_client

from .account import login, get_account_details
from .chest import (
    get_loot, get_key_fragment_count,
    get_key_count, get_generic_chest_count,
    open_generic_chests, forge)
from .exceptions import CompletedAccount


def get_macro(status):
    ''' Returns which macro to run '''
    if 'client_open' not in status:
        return 'open_client'
    if 'should_change_account' in status:
        return 'restart_client'
    if 'login_succeed' in status:
        return 'do_client_tasks'
    if ('login_succeed' not in status and
            'login_in_progress' not in status):
        return 'login'
    if 'banned' in status:
        raise CompletedAccount
    return 'wait'


def do_client_tasks(connection, account):
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
    get_account_details(connection, account)
    raise CompletedAccount


def do_macro(connection, macro, account):
    ''' Runs a macro using the handler mapping '''
    handlers = {
        'login': [login, (connection, account)],
        'do_client_tasks': [do_client_tasks, (connection, account)],
        'open_client': [open_league_client, ()],
        'restart_client': [restart_league_client, ()],
    }
    if macro not in handlers:
        return {'error': 'Macro not implemented'}
    return handlers[macro][0](*handlers[macro][1])
