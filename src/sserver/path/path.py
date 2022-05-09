"""Handles path operations.

This module provides useful functions to aid with locating files in a dynamic
environment.
"""

import os
import sys
from typing import List, Union


def get_path_to_parent(parent_folder: str) -> Union[str, None]:
    """Get the path to the cloests directory with name `parent_folder`.

    Args:
        parent_folder (`str`): The name of the parent directory to find.

    Note:
        This will only return the first folder with name `parent_folder`.

    Returns:
        `str` | `None`: The path to the closest directory with name
            `parent_folder` or None if not found.
    """

    for root, dirs, files in os.walk(os.getcwd()):
        if parent_folder in dirs:
            return os.path.join(root, parent_folder)

    return None


def get_directory_list(directory: str) -> List[str]:
    """Get a list of the directories in `directory`.

    Args:
        directory (`str`): The directory to search in.

    Returns:
        `List[str]`: The list of directories.
    """

    if os.path.exists(directory):
        return [
            subdirectory
            for subdirectory in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, subdirectory))
        ]

    return []


def get_path_list_to_file(filename: str, base_path: str = sys.path[0],
                          folder_list: str = None,
                          include_parent_folder: bool = False) -> List[str]:
    """Get a list of paths pointing at a file with name `filename`.

    Args:
        filename (`str`): The filename to search for.
        base_path (`str`, optional): The path to begin searching in.
            Defaults to sys.path[0].
        folder_list (`str`, optional): A list of folders to search in.
            Defaults to None.
        include_parent_folder (`bool`, optional): Whether to include the
            parent folder in the returned path. Defaults to False.

    Note:
        If `folder_list` is set, only those folders will be searched in.

    Returns:
        `List[str]`: The list of paths to files with name `filename`.
    """

    path_list = []

    if folder_list is not None:
        for folder in folder_list:
            path_list.extend(
                get_path_list_to_file(
                    filename,
                    base_path=os.path.join(base_path, folder),
                    folder_list=None,
                    include_parent_folder=include_parent_folder
                )
            )

        return path_list

    parent_dir = os.path.basename(os.getcwd())

    for root, dirs, files in os.walk(base_path):
        if filename in files:
            if include_parent_folder:
                path_list.append(os.path.join(parent_dir, root, filename))

            else:
                path_list.append(os.path.join(root, filename))

    return path_list
