''' Module to do macro tasks '''
import requests
from process import open_league_client, restart_league_client
from .chest import open_chests
from .exceptions import CompletedAccount


def get_macro(status):
    ''' Returns which macro to run '''
    if 'wrong_account_logged_in' in status:
        return 'restart_client'
    if 'login_succeed' in status:
        return 'open_chests'
    if ('lcu_connected' in status and
            'login_succeed' not in status and
            'login_in_progress' not in status):
        return 'login'
    if 'is_client_open' not in status:
        return 'open_client'
    if 'banned' in status:
        raise CompletedAccount
    return 'wait'


def login(connection, account):
    ''' Login macro '''
    try:
        data = {
            "password": account.password,
            "username": account.username,
        }
        requests.post(connection.url +
                      '/lol-login/v1/session/', **connection.kwargs, json=data)
        return {'description': 'Login request sent'}
    except requests.RequestException:
        return {'error': 'RequestException'}


def do_macro(connection, macro, account):
    ''' Runs a macro using the handler mapping '''
    handlers = {
        'login': [login, (connection, account)],
        'open_chests': [open_chests, (connection, account)],
        'open_client': [open_league_client, ()],
        'restart_client': [restart_league_client, ()],
    }
    if macro not in handlers:
        return {'error': 'Macro not implemented'}
    return handlers[macro][0](*handlers[macro][1])
