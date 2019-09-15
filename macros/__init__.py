''' Module to do macro tasks '''
import requests
from .chest import open_chests
from .exceptions import CompletedAccount


def get_macro(status):
    ''' Returns which macro to run '''
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


HANDLERS = {
    'login': login,
    'open_chests': open_chests,
}


def do_macro(connection, macro, account):
    ''' Runs a macro using the handler mapping '''
    if macro not in HANDLERS:
        return {'error': 'Macro not implemented'}
    return HANDLERS[macro](connection, account)
