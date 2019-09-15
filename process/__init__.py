'''
Module that handles tasks related to processes
'''
import os
import subprocess

import psutil

from settings import LEAGUE_CLIENT_LOCATION, CLIENT_PROCESS_NAME


def is_running(process_name):
    '''
    Check if there is any running process that contains the given name process_name.
    '''
    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if process_name.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def open_league_client():
    '''
    Opens a instance of league client
    '''
    process = subprocess.Popen([LEAGUE_CLIENT_LOCATION, "--headless"])
    return process


def close_league_client():
    '''
    Closes the league client
    '''
    for proc in psutil.process_iter():
        if proc.name() == CLIENT_PROCESS_NAME:
            proc.kill()


def restart_league_client():
    '''
    Restarts the league client
    '''
    close_league_client()
    open_league_client()
