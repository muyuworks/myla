import unittest
from myla import utils


class TestUtils(unittest.TestCase):
    def test_generate_id(self):
        print('uuid:       ', utils.uuid().hex)
        print("sha1:       ", utils.sha1(utils.uuid().bytes).hex())
        print("Id:         ", utils.random_id())
        print("SecretKey:  ", utils.random_key())
