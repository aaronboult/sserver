from sserver.log.Logger import Logger

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
        from os import walk
        from os.path import join

        for root, dirs, files in walk('.'):
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
        from os import walk
        from os.path import join

        path_list = []

        for root, dirs, files in walk('.'):
            if filename in files:
                path_list.append(join(root, filename))

        return path_list