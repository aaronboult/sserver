'''Template class for reading and rendering.'''

from typing import Optional
from os import sep
from os.path import join, exists, isfile, normpath
from sserver.util import log, config


class Template:
    '''The template class for loading and rendering templates.'''

    def __init__(self, template_name: Optional[str] = None,
                 app_name: Optional[str] = None) -> None:
        '''Initializes the template class.'''

        self._template_str = None

        if template_name is not None:
            self.read(template_name, app_name)

    @property
    def template_str(self) -> str:
        '''Gets the template string.

        Returns:
            `str`: The template string.
        '''

        return self._template_str

    def read(self, template_name: str, app_name: Optional[str] = None
             ):
        '''Loads a template from the apps template directory.

        Args:
            template_name (`str`): The name of the template to load.
            app_name (`str`, Optional): The name of the app to load
                the template from. If not passed, app_name will be
                extracted from template_name.

        Returns:
            `Template`: This template object.
        '''

        # Separate the template_name into components (assuming path)
        template_name = normpath(template_name)
        template_name_components = template_name.split(sep)

        # If app_name is not passed, extract it from the template_name
        if app_name is None:
            app_name = template_name_components[0]

        # Reconstruct template name ignoring first component
        template_name = join(*template_name_components[1:])

        APP_FOLDER = config.get('app_folder')
        TEMPLATE_FOLDER = config.get('template_folder', app_name=app_name)
        TEMPLATE_PATH = join(
            APP_FOLDER,
            app_name,
            TEMPLATE_FOLDER,
            template_name
        )

        log.log('app_name', app_name)
        log.log('template_name', template_name)
        log.log('APP_FOLDER', APP_FOLDER)
        log.log('TEMPLATE_FOLDER', TEMPLATE_FOLDER)
        log.log('TEMPLATE_PATH', TEMPLATE_PATH)

        template_str = None

        # Read template file
        if exists(TEMPLATE_PATH):
            if isfile(TEMPLATE_PATH):
                with open(TEMPLATE_PATH) as f:
                    template_str = f.read()

        self._template_str = template_str

        return self
