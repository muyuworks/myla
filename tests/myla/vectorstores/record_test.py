import unittest

from myla.vectorstores import Record


class TestRecord(unittest.TestCase):
    def test_values_to_text(self):
        r = {
            "category": "介绍/推荐",
            "query": "XX系列",
            "response": [
            "XXX"
            ],
            "msg_id": 0,
            "source": "standard"
        }
        t = Record.values_to_text(r, props=['category'])
        self.assertEqual("介绍/推荐", t)

        t = Record.values_to_text(r, props=['category', 'query'])
        self.assertEqual("介绍/推荐\001XX系列", t)

        t = Record.values_to_text(r, props=['category', 'query'], separator='\t')
        self.assertEqual("介绍/推荐\tXX系列", t)

        try:
            Record.values_to_text(r, props='category')
        except Exception as e:
            self.assertTrue(isinstance(e, ValueError))

        t = Record.values_to_text(r, separator='\t')
