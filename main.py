''' Main script of the program '''
import csv
import curses
import os
import threading
import time

import keyboard
from easygui import fileopenbox

from accounts import Account, AccountList
from connection.connection import Connection
from macros import do_macro, get_macro
from macros.exceptions import CompletedAccount
from settings import CSV_DELIMITERS, OUTPUT_DIR
from status import display_status, get_status

BARRIER = threading.Barrier(2)

os.makedirs(OUTPUT_DIR, exist_ok=True)


def terminate():
    ''' Terminates the script '''
    BARRIER.wait()


def main(stdscr):
    ''' Main function of the program '''
    output = ''
    file_path = fileopenbox(
        'Open account data csv, ctrl+shift+q to exit')
    if file_path is None:
        terminate()

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
        start_time = time.time()
        stdscr.clear()
        status = get_status(connection)
        try:
            macro = get_macro(status)
            output = do_macro(connection, macro, current)
        except CompletedAccount:
            account_list.complete()
            output = {'description': 'Completed'}

        process_time = time.time() - start_time
        stdscr.addstr('{:<30}{:.5f}s\n'.format('Process time', process_time))
        display_status(stdscr, status)
        stdscr.addstr('\n{:<30}{}\n'.format('Username', current.username))
        stdscr.addstr('{:<30}{}\n'.format('Password', current.password))
        stdscr.addstr('{:<30}{}\n'.format('Macro', macro))
        stdscr.addstr('{:<30}{}\n'.format('Ouptut', output))
        stdscr.addstr('\nctrl+shift+q to exit\n')
        stdscr.refresh()
        time.sleep(1)


if __name__ == '__main__':
    threading.Thread(target=curses.wrapper, args=(main,), daemon=True).start()
    keyboard.add_hotkey('ctrl+shift+q', terminate)
    terminate()
