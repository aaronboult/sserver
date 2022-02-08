import sys


#
# Empty Placeholder
#
class __Empty__:
    pass


#
# Logger
#
class Logger:


    #
    # Delimiter
    #
    delimiter = ' : '


    #
    # Info
    # @param str text The text to log
    # @param dict context (optional) Context to go along with text
    #
    @staticmethod
    def info(text, context = __Empty__):

        if not isinstance(text, str):
            raise TypeError(f'text must be of type str, got {type(text)}')

        sys.stdout.write(text)

        if context != __Empty__:
            sys.stdout.write(Logger.delimiter + Logger.format(context))

        sys.stdout.write('\n')


    #
    # Log
    # @param str text The text to log
    # @param dict context (optional) Context to go along with text
    #
    @staticmethod
    def log(text, context = __Empty__):

        Logger.info(Logger.format(text), context)
    

    #
    # Label
    # @param str text The text to label
    #
    @staticmethod
    def label(text, context = __Empty__):

        if not isinstance(text, str):
            raise TypeError(f'text must be of type str, got {type(text)}')

        length = len(text)

        hash_bars = '#' * (length + 4)

        text = f'\n{hash_bars}\n# {text} #\n{hash_bars}\n\n'

        sys.stdout.write(text)

        if context != __Empty__:
            sys.stdout.write(Logger.format(context))
    

    #
    # Exception
    # @param Error error The error to log
    #
    @staticmethod
    def exception(error):
        if not isinstance(error, Exception):
            raise TypeError(f'error must be of type Exception, got {type(error)}')

        Logger.label(f'Exception')
        Logger.log(str(error))
        Logger.linebreak()
    

    #
    # Linebreak
    #
    @staticmethod
    def linebreak(count = 1):
        sys.stdout.write('\n' * count)


    #
    # Format text
    # @param str content The content to format
    # @param **kwargs Options for processing
    # @returns str The formatted content
    #
    @staticmethod
    def format(content, **kwargs):

        text = None

        if type(content) == dict:
            return Logger.format_dict(content, **kwargs)

        if type(content) == list:
            return Logger.format_list(content, **kwargs)
        
        if type(content) == tuple:
            return Logger.format_tuple(content, **kwargs)
        
        if type(content) == set:
            return Logger.format_set(content, **kwargs)
        
        if type(content) == str:
            text = f'"{str(content)}"'

        else:
            text = str(content)

        return text


    #
    # Format Dict
    # @param dict dct The dictionary to format
    # @param **kwargs Options for processing
    # @returns str The formatted dictionary
    #
    @staticmethod
    def format_dict(dct, **kwargs):
        if not isinstance(dct, dict):
            raise TypeError(f'dct must be of type dict, got {type(dct)}')

        # Update indent level for tabbing
        indent_level = kwargs.get('indent_level', 0)

        text = '{\n'
        
        for key, value in dct.items():
            kwargs['indent_level'] = indent_level + 1
            current_indent = '\t' * (indent_level + 1)

            text += f'{current_indent}"{key}"{Logger.delimiter}{Logger.format(value, **kwargs)},\n'

        if text == '{\n':
            text = '\t' * (indent_level - 1) + '{}'

        else:
            text += '\t' * (indent_level) + '}'

        return text


    #
    # Format List
    # @param list lst The list to format
    # @param **kwargs Options for processing
    # @returns str The formatted list
    #
    @staticmethod
    def format_list(lst, **kwargs):
        if not isinstance(lst, list):
            raise TypeError(f'lst must be of type list, got {type(lst)}')

        kwargs['wrappers'] = ('[', ']')

        return Logger.format_iterable(lst, **kwargs) 
    


    #
    # Format Tuple
    # @param tuple tpl The tuple to format
    # @param **kwargs Options for processing
    # @returns str The formatted tuple
    #
    @staticmethod
    def format_tuple(tpl, **kwargs):
        if not isinstance(tpl, tuple):
            raise TypeError(f'tpl must be of type tuple, got {type(tpl)}')

        kwargs['wrappers'] = ('(', ')')

        return Logger.format_iterable(tpl, **kwargs)
    

    #
    # Format Set
    # @param set s The set to format
    # @param **kwargs Options for processing
    # @returns str The formatted set
    #
    @staticmethod
    def format_set(st, **kwargs):
        if not isinstance(st, set):
            raise TypeError(f's must be of type set, got {type(st)}')

        kwargs['wrappers'] = ('{', '}')

        return Logger.format_iterable(tuple(st), **kwargs)
    


    #
    # Format Iterable
    # @param iterable itr The iterable to format
    # @param **kwargs Options for processing
    # @returns str The formatted iterable
    #
    @staticmethod
    def format_iterable(itr, **kwargs):

        use_multiline = kwargs.get('use_multiline', True)

        # Expects a tuple e.g. ("[", "]")
        wrappers = kwargs.get('wrappers')

        text = wrappers[0]

        if use_multiline:
            indent_level = kwargs.get('indent_level', 0)

        for i in range(len(itr)):
            trail = ''

            if i > 0 or use_multiline:
                trail = ','

            if use_multiline:
                kwargs['indent_level'] = indent_level + 1
                text += '\n' + '\t' * (indent_level + 1)

            text += f'{Logger.format(itr[i], **kwargs)}{trail}'

        if use_multiline:
            text += '\n' + '\t' * (indent_level)

        text += wrappers[1]

        return text