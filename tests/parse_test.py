from sserver.parse import parse
from sserver.util import log

if __name__ == '__main__':

    input_string = 'pi == pi'

    context = {
        'a' : 1,
        'b' : 2,
        'c' : 3,
        'd' : 4,
        'e' : {
            'f' : {
                'g' : {
                    'h' : 5,
                }
            }
        }
    }

    log.log(parse.parse_string_to_value(context, input_string))