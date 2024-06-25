from random import randint
from typing import List

from xinference_client import RESTfulClient as Client

from ._embeddings import Embeddings


class XinferenceEmbeddings(Embeddings):
    def __init__(
            self,
            base_url,
            model_id,
            instruction=None
        ) -> None:
        self._base_url = base_url
        self._model_id = model_id
        self._instruction = instruction

        client = Client(self._base_url)
        #self._model = client.get_model(model_id)
        model_ids = model_id.split(",")
        self._models = []
        for m_id in model_ids:
            self._models.append(client.get_model(m_id))

    def embed_batch(self, texts: List[str], **kwargs) -> List[List[float]]:
        if self._instruction is not None:
            texts = [self._instruction + t for t in texts]

        model = self._get_model()

        embeds = model.create_embedding(texts)
        return [e["embedding"] for e in embeds["data"]]

    def _get_model(self):
        idx = randint(0, len(self._models) - 1)
        return self._models[idx]
