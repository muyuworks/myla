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
        self._model = client.get_model(model_id)

    def embed_batch(self, texts: List[str], **kwargs) -> List[List[float]]:
        if self._instruction is not None:
            texts = [self._instruction + t for t in texts]

        embeds = self._model.create_embedding(texts)
        return [e["embedding"] for e in embeds["data"]]
