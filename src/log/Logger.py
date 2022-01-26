import sys

class Logger:

    #
    # Delimiter
    #
    delimiter = ' : '

    #
    # Log
    #
    @classmethod
    def log(cls, text, context = None):
        
        sys.stdout.write(cls.format(text))

        if context is not None:
            sys.stdout.write(cls.delimiter + cls.format(context))

        sys.stdout.write('\n')

    


    #
    # Format text
    #
    @classmethod
    def format(cls, text):

        text = str(text)

        # @todo Format

        return text