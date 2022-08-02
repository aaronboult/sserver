"""Manages static files."""


import os, sys
from sserver.path import path
from sserver.util import config, log


def load():
    """Load static files ready for the server."""

    # Get each app and locate static path (if exists)
    APP_FOLDER = config.get('app_folder')
    APP_DIRECTORY_PATH = os.path.join(sys.path[0], APP_FOLDER)
    APP_DIRECTORY_LIST = path.get_directory_list(APP_DIRECTORY_PATH)

    log.log('app list', APP_DIRECTORY_LIST)

    for APP in APP_DIRECTORY_LIST:

        # Get app static config
        APP_CONFIG = config.get