from distutils.log import Log
import unittest

# Imports
from log.Logger import Logger

class LoggerTest(unittest.TestCase):


    #
    # Test Format Int
    #
    def test_format_int(self):
        self.assertEqual(Logger.format(10), '10')


    #
    # Test Format Float
    #
    def test_format_float(self):
        self.assertEqual(Logger.format(10.5), '10.5')


    #
    # Test Format None
    #
    def test_format_none(self):
        self.assertEqual(Logger.format(None), 'None')


    #
    # Test Format True
    #
    def test_format_true(self):
        self.assertEqual(Logger.format(True), 'True')


    #
    # Test Format False
    #
    def test_format_false(self):
        self.assertEqual(Logger.format(False), 'False')


    #
    # Test Format String
    #
    def test_format_str(self):
        self.assertEqual(Logger.format('test'), '"test"')


    #
    # Test Format List
    #
    def test_format_list(self):
        lst = [
            'l1',
            'l2',
            'l3',
        ]

        expected = '''[
\t"l1",
\t"l2",
\t"l3",
]'''

        self.assertEqual(Logger.format_list(lst), expected)


    #
    # Test Format Tuple
    #
    def test_format_tuple(self):
        tpl = (
            't1',
            't2',
            't3',
        )

        expected = '''(
\t"t1",
\t"t2",
\t"t3",
)'''

        self.assertEqual(Logger.format_tuple(tpl), expected)


    #
    # Test Format Set
    #
    def test_format_set(self):
        st = {
            's1',
            's2',
            's3',
        }

        expected = '''{
\t"s1",
\t"s2",
\t"s3",
}'''

        self.assertEqual(Logger.format_set(st), expected)


    #
    # Test Format Dict
    #
    def test_format_dict(self):
        
        dct = {
            'k1' : 'v1',
            'k2' : {
                'i1' : 'vi1',
            },
            'k3' : {
                'i1' : {
                    'i2' : {
                        'ki2' : 'vi2',
                    },
                    'ki1' : 'vi1',
                },
            },
        }
        
        expected = '''{
\t"k1" : "v1",
\t"k2" : {
\t\t"i1" : "vi1",
\t},
\t"k3" : {
\t\t"i1" : {
\t\t\t"i2" : {
\t\t\t\t"ki2" : "vi2",
\t\t\t},
\t\t\t"ki1" : "vi1",
\t\t},
\t},
}'''

        self.assertEqual(Logger.format_dict(dct), expected)

if __name__ == '__main__':
    unittest.main()