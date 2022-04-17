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
    @staticmethod
    def get_path_list_to_file(filename):

        parent_dir = basename(getcwd())

        path_list = []
        for root, dirs, files in walk('.'):
            if filename in files:
                path_list.append(join(parent_dir, root, filename))

        return path_list