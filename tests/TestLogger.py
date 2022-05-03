import unittest

# Package Imports
from sserver.log.Logger import Logger


#
# Logger Tests
#
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
        # The order of the items in the set is not guaranteed, so multiple expected

        st = {
            's1',
            's2',
            's3',
        }

        expected_posibilities = []

        unordered_lines = [
            '\t"s1"',
            '\t"s2"',
            '\t"s3"',
        ]

        number_of_lines = len(unordered_lines)

        # Create an expected value for each permutation of the lines
        for i in range(number_of_lines):
            for j in range(number_of_lines):
                for k in range(number_of_lines):
                    if i != j and i != k and j != k:
                        expected_posibilities.append('{\n' + unordered_lines[i] + ',\n' + unordered_lines[j] + ',\n' + unordered_lines[k] + ',\n}')

        self.assertIn(Logger.format_set(st), expected_posibilities)


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