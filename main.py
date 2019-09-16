''' Main script of the program '''
import csv
import curses
import os
import threading
import time

import keyboard
from easygui import fileopenbox
from requests.exceptions import RequestException


from accounts import Account, AccountList
from connection.connection import Connection
from macros import do_macro, get_macro
from macros.exceptions import CompletedAccount, LootRetrieveException, BadResponseException
from settings import CSV_DELIMITERS, OUTPUT_DIR, ACTION_INTERVAL
from status import display_status, get_status
from process import close_league_client

BARRIER = threading.Barrier(2)

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, 'chests'), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, 'accounts'), exist_ok=True)


def terminate():
    ''' Terminates the script '''
    BARRIER.wait()


def main(stdscr):
    ''' Main function of the program '''
    output = ''
    file_path = fileopenbox('Open account data csv')
    if file_path is None:
        terminate()
        return

    account_list = AccountList()
    with open(file_path, newline='') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024), delimiters=CSV_DELIMITERS)
        csvfile.seek(0)
        reader = csv.DictReader(csvfile, dialect=dialect)
        for row in reader:
            account_list.append(Account(row['username'], row['password']))

    connection = Connection()
    while True:
        current = account_list.current()
        if current is None:
            terminate()
            return
        start_time = time.time()
        stdscr.clear()
        status = []
        macro = None
        try:
            status = get_status(connection, current)
            try:
                macro = get_macro(status)
                output = do_macro(connection, macro, current)
            except CompletedAccount:
                account_list.complete()
                output = {'description': 'Completed'}
        except RequestException as err:
            output = {'error': 'RequestException: {0}'.format(err)}
        except BadResponseException:
            output = {'error': 'BadResponseException'}
        except LootRetrieveException:
            output = {'error': 'LootRetrieveException'}

        process_time = time.time() - start_time
        stdscr.addstr('{:<30}{:.5f}s\n'.format('Process time', process_time))
        display_status(stdscr, status)
        stdscr.addstr('\n{:<30}{}\n'.format('Username', current.username))
        stdscr.addstr('{:<30}{}\n'.format('Password', current.password))
        stdscr.addstr('{:<30}{}\n'.format('Macro', macro))
        stdscr.addstr('{:<30}{}\n'.format('Ouptut', output))
        stdscr.addstr('\nctrl+shift+q to exit')
        stdscr.refresh()
        time.sleep(ACTION_INTERVAL)


if __name__ == '__main__':
    threading.Thread(target=curses.wrapper, args=(main,), daemon=True).start()
    keyboard.add_hotkey('ctrl+shift+q', terminate)
    terminate()
    close_league_client()
