import unittest

from myla import llms
from myla import utils


class TestMockLLM(unittest.TestCase):
    def test_chat(self):
        llm = llms.get("mock@mock")
        self.assertIsNotNone(llm)

        g = utils.sync_call(llm.chat, messages=[{'role': 'user', 'content': 'hello'}])
        self.assertEqual('hello', g)

        g = utils.sync_call(llm.generate, instructions="hello")
        self.assertEqual('hello', g)
