import unittest

from myla.vectorstores.xinference_embeddings import XinferenceEmbeddings


class XinferenceTests(unittest.TestCase):
    def test_connect(self):
        embed = XinferenceEmbeddings(
            base_url="http://localhost:9997",
            model_id="bge-small-zh",
            instruction="Represent the sentence for searching the most similar sentences from the corpus."
        )
        embeds = embed.embed("你好")
        self.assertEqual(len(embeds), 512)
