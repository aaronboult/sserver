import os
import sys
from sserver.log.Logger import Logger
from os import walk, getcwd
from os.path import join, basename

#
# Path Tools
#
class PathTools:


    #
    # Get Path To Parent
    # @param str parent_folder The name of the folder to search for
    # @param str/None The path to the parent folder, or none if not found
    #
    @staticmethod
    def get_path_to_parent(parent_folder):
        for root, dirs, files in walk(getcwd()):
            if parent_folder in dirs:
                return join(root, parent_folder)
        
        return None


    #
    # Get Path List To File
    # @param str filename The name of the file to search for
    # @returns list The list of paths to files of the given name
    #
    @classmethod
    def get_path_list_to_file(cls, filename, base_path = sys.path[0], folder_list = None, include_parent_folder = False):

        path_list = []

        if folder_list is not None:
            for folder in folder_list:
                path_list.extend(
                    cls.get_path_list_to_file(
                        filename,
                        base_path = os.path.join(base_path, folder),
                        folder_list = None,
                        include_parent_folder = include_parent_folder
                    )
                )
            return path_list

        parent_dir = basename(getcwd())

        for root, dirs, files in walk(base_path):
            if filename in files:
                if include_parent_folder:
                    path_list.append(join(parent_dir, root, filename))

                else:
                    path_list.append(join(root, filename))

        return path_list