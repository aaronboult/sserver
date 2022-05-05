import unittest


from sserver.util import log


class LoggerTest(unittest.TestCase):
    """Unittest the sserver.util.log module."""


    def test_format_int(self):
        """Test sserver.util.log.format_int."""

        self.assertEqual(log.format(10), '10')


    def test_format_float(self):
        """Test sserver.util.log.format_float."""

        self.assertEqual(log.format(10.5), '10.5')


    def test_format_none(self):
        """Test sserver.util.log.format, passing None."""

        self.assertEqual(log.format(None), 'None')


    def test_format_true(self):
        """Test sserver.util.log.format, passing True."""

        self.assertEqual(log.format(True), 'True')


    def test_format_false(self):
        """Test sserver.util.log.format, passing False."""

        self.assertEqual(log.format(False), 'False')


    def test_format_str(self):
        """Test sserver.util.log.format, passing a string."""

        self.assertEqual(log.format('test'), '"test"')


    def test_format_list(self):
        """Test sserver.util.log.format_list."""

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

        self.assertEqual(log.format_list(lst), expected)


    def test_format_tuple(self):
        """Test sserver.util.log.format_tuple."""

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

        self.assertEqual(log.format_tuple(tpl), expected)


    def test_format_set(self):
        """Test sserver.util.log.format_set."""

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

        self.assertIn(log.format_set(st), expected_posibilities)


    def test_format_dict(self):
        """Test sserver.util.log.format_dict."""
        
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

        self.assertEqual(log.format_dict(dct), expected)