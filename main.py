''' Main script of the program '''
import csv
import curses
import threading
import time

import keyboard
from easygui import fileopenbox

from connection.connection import Connection
from settings import CSV_DELIMITERS
from status import display_status, get_status


def main(stdscr):
    ''' Main function of the program '''
    output = ''
    while True:
        file_path = fileopenbox(
            'Open account data csv, ctrl+shift+q to exit')
        if file_path is not None:
            break

    with open(file_path, newline='') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024), delimiters=CSV_DELIMITERS)
        csvfile.seek(0)
        reader = csv.DictReader(csvfile, dialect=dialect)
        for row in reader:
            print(row['username'], row['password'])

    connection = Connection()
    while True:
        start_time = time.time()
        stdscr.clear()
        status = get_status(connection)
        process_time = time.time() - start_time
        stdscr.addstr('{:<30}{:.5f}s\n'.format('Process time', process_time))
        display_status(stdscr, status)
        stdscr.addstr('\n{:<30}{}\n'.format('Ouptut', output))
        stdscr.addstr('\nctrl+shift+q to exit\n')
        stdscr.refresh()
        time.sleep(1)


if __name__ == '__main__':
    threading.Thread(target=curses.wrapper, args=(main,), daemon=True).start()
    keyboard.wait('ctrl+shift+q')
