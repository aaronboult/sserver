"""Manages static files."""


import os, sys
from sserver.path import path
from sserver.util import config, log


def load():
    """Load static files ready for the server."""

    log.info('Loading static files...')

    # Get each app and locate static path (if exists)
    APP_FOLDER = config.get('app_folder')
    APP_DIRECTORY_PATH = os.path.join(sys.path[0], APP_FOLDER)
    APP_DIRECTORY_LIST = path.get_directory_list(APP_DIRECTORY_PATH)

    log.log('APP_FOLDER', APP_FOLDER)
    log.log('APP_DIRECTORY_PATH', APP_DIRECTORY_PATH)
    log.log('APP_DIRECTORY_LIST', APP_DIRECTORY_LIST)

    for APP in APP_DIRECTORY_LIST:

        # Get app static config
        APP_CONFIG = config.get_app_config(APP)

        if APP_CONFIG is not None:
            APP_PATH = os.path.join(APP_FOLDER, APP)

            # Resolve static paths
            STATIC_IMAGE_FOLDER = os.path.join(APP_PATH, APP_CONFIG.get('static_image_folder'))
            STATIC_CSS_FOLDER = os.path.join(APP_PATH, APP_CONFIG.get('static_css_folder'))
            STATIC_JS_FOLDER = os.path.join(APP_PATH, APP_CONFIG.get('static_js_folder'))

            log.log('STATIC_IMAGE_FOLDER', STATIC_IMAGE_FOLDER)
            log.log('STATIC_CSS_FOLDER', STATIC_CSS_FOLDER)
            log.log('STATIC_JS_FOLDER', STATIC_JS_FOLDER)

            # Duplicate static file structure into static folder
            # Cache static file paths to get url in tempaltes etc.