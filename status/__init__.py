''' Module to find the status of league client '''
from requests.exceptions import RequestException

from process import is_running
from settings import CLIENT_PROCESS_NAME

BUGGED_DESCRIPTION = (
    'RSO Server error: '
    'Error response for POST /lol-rso-auth/v1/authorization/gas: '
    'server_error: Received invalid JSON'
)


def is_client_open(*_):
    ''' Returns if client is open '''
    if not is_running(CLIENT_PROCESS_NAME):
        return []
    return ['client_open']


def is_client_connected(connection, *_):
    ''' Returns if client is connected '''
    if connection.url is None:
        return []
    return ['client_connected']


def is_lcu_connected(connection, status, *_):
    ''' Returns if lcu is connected '''
    if 'client_connected' not in status:
        return []
    if connection.url is None:
        return []
    try:
        res = connection.get('/lol-service-status/v1/lcu-status/')
    except RequestException:
        return []
    if res.status_code == 404:
        return []
    res_json = res.json()
    try:
        if res_json['status'] == 'online':
            return ['lcu_connected']
    except KeyError:
        pass
    return []


def check_login_session(connection, status, *_):
    ''' Checks login session and returns status '''
    if 'lcu_connected' not in status:
        return []
    if connection.url is None:
        return []
    try:
        res = connection.get('/lol-login/v1/session/')
    except RequestException:
        return []
    res_json = res.json()
    output = []
    if 'state' in res_json:
        if res_json['isNewPlayer']:
            output.append('new_player')
        if res_json['state'] == 'SUCCEEDED':
            output.append('login_succeed')
        if res_json['state'] == 'ERROR':
            if res_json['error']['messageId'] == 'ACCOUNT_BANNED':
                output.append('banned')
            if res_json['error']['description'] == BUGGED_DESCRIPTION:
                output.append('possibly_bugged')
        if res_json['state'] == 'IN_PROGRESS':
            output.append('login_in_progress')
    return output


def is_leaverbuster_warning(connection, status, *_):
    ''' Returns if leaverbuster warning exists '''
    if 'login_succeed' not in status:
        return []
    if connection.url is None:
        return []
    try:
        res = connection.get('/lol-leaver-buster/v1/notifications/')
    except RequestException:
        return []
    res_json = res.json()
    for notification in res_json:
        if notification['type'] == 'TaintedWarning':
            return ['leaverbuster_warning']
    return []


def is_wrong_account(connection, status, account):
    ''' Returns if wrong account is logged in  '''
    if 'login_succeed' not in status:
        return []
    if connection.url is None:
        return []
    try:
        res = connection.get('/lol-login/v1/login-platform-credentials/')
    except RequestException:
        return []
    res_json = res.json()
    if res_json['username'].lower() != account.username.lower():
        return ['wrong_account_logged_in']
    return []


STATUS_LIST = [
    'client_open',
    'client_connected',
    'lcu_connected',
    'login_in_progress',
    'login_succeed',
    'wrong_account_logged_in',
    'banned',
]

STATUS_FUNCTIONS = [
    is_client_open,
    is_client_connected,
    is_lcu_connected,
    check_login_session,
    is_wrong_account,
]


def get_status(connection, account):
    ''' Returns the status of league client '''
    status = []
    for func in STATUS_FUNCTIONS:
        status += func(connection, status, account)
    return status


def display_status(stdscr, status):
    ''' Displays the status in the screen '''
    for key in STATUS_LIST:
        title = key.replace('_', ' ').capitalize()
        stdscr.addstr('{:<30}{}\n'.format(title, key in status))
