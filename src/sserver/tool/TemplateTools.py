from jinja2 import Environment, PackageLoader, select_autoescape
from sserver.log.Logger import Logger
from sserver.tool.ConfigTools import ConfigTools


#
# Template Tools
#
class TemplateTools:


    #
    # Fetch
    # @param string app_name The name of the app to fetch from
    # @param string template_name The name of the template to fetch from
    # @returns Template The template object
    #
    @staticmethod
    def fetch(app_name, template_name):

        APP_FOLDER = ConfigTools.fetch('APP_FOLDER')
        TEMPLATE_FOLDER = ConfigTools.fetch('TEMPLATE_FOLDER', app_name = app_name)
        TEMPLATE_FOLDER_PATH = f'{APP_FOLDER}.{app_name}'

        Logger.log('app_name', app_name)
        Logger.log('templates_folder', TEMPLATE_FOLDER)

        try:
            environment = Environment(
                loader = PackageLoader(TEMPLATE_FOLDER_PATH, TEMPLATE_FOLDER),
                autoescape = select_autoescape()
            )

            return environment.get_template(template_name)

        except Exception as exception:
            Logger.exception(exception)

        return None


    #
    # Render
    # @param Template template The template object
    # @param dict context The context to render the template with
    # @returns string The rendered template
    #
    @staticmethod
    def render(template, context):
        return template.render(**context)
    

    #
    # Load Template
    # @param **kwargs The template values
    # @returns string The rendered template 
    #
    @classmethod
    def load(cls, **kwargs):

        app_name = kwargs.get('app_name')
        if app_name == None:
            raise TypeError('app_name must be set')

        elif not isinstance(app_name, str):
            raise TypeError('app_name must be of type str')


        template_name = kwargs.get('template_name')
        if template_name == None:
            raise TypeError('template_name must be set')

        elif not isinstance(template_name, str):
            raise TypeError('template_name must be of type str')
        
        context = kwargs.get('context', {})
        if not isinstance(context, dict):
            raise TypeError('context must be of type dict')
        
        template = cls.fetch(app_name, template_name)

        return cls.render(template, context)