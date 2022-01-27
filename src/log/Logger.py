import sys

class Logger:


    #
    # Delimiter
    #
    delimiter = ' : '


    #
    # Log
    # @param str text The test to log
    # @param dict context (optional) Context to go along with text
    #
    @classmethod
    def log(cls, text, context = None):
        
        sys.stdout.write(cls.format(text))

        if context is not None:
            sys.stdout.write(cls.delimiter + cls.format(context))

        sys.stdout.write('\n')


    #
    # Format text
    # @param str content The content to format
    # @param **kwargs Options for processing
    # @returns str The formatted content
    #
    @classmethod
    def format(cls, content, **kwargs):

        text = None

        if type(content) == dict:
            return cls.format_dict(content, **kwargs)

        if type(content) == list:
            return cls.format_list(content, **kwargs)
        
        if type(content) == tuple:
            return cls.format_tuple(content, **kwargs)
        
        if type(content) == set:
            return cls.format_set(content, **kwargs)
        
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
    @classmethod
    def format_dict(cls, dct, **kwargs):

        # Update indent level for tabbing
        indent_level = kwargs.get('indent_level', 0)

        text = '{\n'
        
        for key, value in dct.items():
            kwargs['indent_level'] = indent_level + 1
            current_indent = '\t' * (indent_level + 1)

            text += f'{current_indent}"{key}"{cls.delimiter}{cls.format(value, **kwargs)},\n'

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
    @classmethod
    def format_list(cls, lst, **kwargs):
        kwargs['wrappers'] = ('[', ']')

        return cls.format_iterable(lst, **kwargs) 
    


    #
    # Format Tuple
    # @param tuple tpl The tuple to format
    # @param **kwargs Options for processing
    # @returns str The formatted tuple
    #
    @classmethod
    def format_tuple(cls, tpl, **kwargs):
        kwargs['wrappers'] = ('(', ')')

        return cls.format_iterable(tpl, **kwargs)
    

    #
    # Format Set
    # @param set s The set to format
    # @param **kwargs Options for processing
    # @returns str The formatted set
    #
    @classmethod
    def format_set(cls, st, **kwargs):
        kwargs['wrappers'] = ('{', '}')

        return cls.format_iterable(tuple(st), **kwargs)
    


    #
    # Format Iterable
    # @param iterable itr The iterable to format
    # @param **kwargs Options for processing
    # @returns str The formatted iterable
    #
    @classmethod
    def format_iterable(cls, itr, **kwargs):
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

            text += f'{cls.format(itr[i], **kwargs)}{trail}'

        if use_multiline:
            text += '\n' + '\t' * (indent_level)

        text += wrappers[1]

        return text