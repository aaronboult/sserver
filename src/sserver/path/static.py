"""Manages static files."""


import mimetypes
import os
import sys
from typing import Optional
from typing import Union
from sserver.path import path
from sserver.util import cache
from sserver.util import config
from sserver.util import log
from shutil import copy


def load():
    """Load static files ready for the server."""

    log.info('Loading static files...')

    # Get each app and locate static path (if exists)
    STATIC_FOLDER = config.get('static_folder')
    APP_FOLDER = config.get('app_folder')
    APP_DIRECTORY_PATH = os.path.join(sys.path[0], APP_FOLDER)
    APP_DIRECTORY_LIST = path.get_directory_list(APP_DIRECTORY_PATH)

    # Ensure STATIC_FOLDER directory exists
    if not os.path.isdir(STATIC_FOLDER):
        os.mkdir(STATIC_FOLDER)

    static_path_map = {}

    for APP in APP_DIRECTORY_LIST:

        # Get app static config
        APP_CONFIG = config.get_app_config(APP, use_default=True)
        APP_PATH = os.path.join(APP_FOLDER, APP)

        # Resolve static paths
        PATH_TO_CLONE_LIST = [
            os.path.join(APP_PATH, APP_CONFIG.get('static_image_folder')),
            os.path.join(APP_PATH, APP_CONFIG.get('static_css_folder')),
            os.path.join(APP_PATH, APP_CONFIG.get('static_js_folder')),
        ]

        for PATH_TO_CLONE in PATH_TO_CLONE_LIST:

            STATIC_PATH = os.path.join(STATIC_FOLDER, PATH_TO_CLONE)

            # Ensure static folder for app exists
            if not os.path.isdir(STATIC_PATH):
                os.makedirs(STATIC_PATH)

            # Iterate over files and copy to static folder
            # Preserve subdirectory structure
            for ROOT, _, FILE_LIST in os.walk(PATH_TO_CLONE):
                for FILE in FILE_LIST:
                    FILE_PATH = os.path.join(ROOT, FILE)
                    RELATIVE_PATH = os.path.relpath(
                        FILE_PATH,
                        PATH_TO_CLONE,
                    )

                    # @future Config value for copying static files to different directory
                    # # Ensure file directory exists in static folder
                    # STATIC_FILE_DESTINATION = os.path.join(
                    #     STATIC_PATH,
                    #     RELATIVE_PATH,
                    # )
                    # STATIC_FILE_DESTINATION_DIR = os.path.dirname(
                    #     STATIC_FILE_DESTINATION
                    # )

                    # if not os.path.isdir(STATIC_FILE_DESTINATION_DIR):
                    #     os.makedirs(
                    #         os.path.dirname(STATIC_FILE_DESTINATION)
                    #     )

                    # static_file_path = copy(
                    #     FILE_PATH,
                    #     STATIC_FILE_DESTINATION,
                    # )

                    # Add to static path map
                    static_file_key = os.path.join(
                        PATH_TO_CLONE,
                        RELATIVE_PATH,
                    ).replace(APP_FOLDER, '')

                    static_path_map[static_file_key] = FILE_PATH

    log.info('Static Path Map', static_path_map)

    cache.set('__static__', static_path_map)


def get_static_file_path(path: str) -> str:
    """Get a static file path.

    Args:
        path (`str`): The path to get.
    """

    static_path = cache.get('__static__').get(path)

    # If no static file was found, reload files in an attempt to find it
    if static_path is None:
        load()
        static_path = cache.get('__static__').get(path)

    return static_path


def is_static_file(path: str) -> bool:
    """Check if a path is a static file.

    Args:
        path (`str`): The path to check.
    """

    return get_static_file_path(path) is not None


def get_static_file_contents(path: str) -> Optional[Union[str, str]]:
    """Get a static files contents.

    Args:
        path (`str`): The path to get.
    """

    static_path = get_static_file_path(path)

    if static_path is not None:
        with open(static_path, 'r') as static_file:
            return static_file.read(), static_path

    return None


def get_static_file(path: str) -> str:
    """Get a static file with contents and headers.

    Args:
        path (`str`): The path to get.
    """

    static_file_contents, static_file_path = get_static_file_contents(path)

    # Determine content type
    mime_type = mimetypes.guess_type(static_file_path)[0]

    # Return static file
    return {
        'body': static_file_contents,
        'headers': [
            ('Content-Type', mime_type),
        ],
    }
