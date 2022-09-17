'''Template class for reading and rendering.'''

from __future__ import annotations
from os.path import join, exists, isfile
from sserver.util import log, config


class Template:
    '''The template class for loading and rendering templates.'''

    def __init__(self) -> None:
        '''Initializes the template class.'''

        self._template_str = None

    @property
    def template_str(self) -> str:
        '''Gets the template string.

        Returns:
            `str`: The template string.
        '''

        return self._template_str

    def read(self, app_name: str, template_name: str) -> Template:
        '''Loads a template from the apps template directory.

        Args:
            app_name (`str`): The name of the app to load the template from.
            template_name (`str`): The name of the template to load.

        Returns:
            `Template`: This template object.
        '''

        APP_FOLDER = config.get('app_folder')
        TEMPLATE_FOLDER = config.get('template_folder', app_name=app_name)
        TEMPLATE_PATH = join(
            APP_FOLDER,
            app_name,
            TEMPLATE_FOLDER,
            template_name
        )

        log.log('TEMPLATE_PATH', TEMPLATE_PATH)

        template_str = None

        # Read template file
        if exists(TEMPLATE_PATH):
            if isfile(TEMPLATE_PATH):
                with open(TEMPLATE_PATH) as f:
                    template_str = f.read()

        self._template_str = template_str

        return self
