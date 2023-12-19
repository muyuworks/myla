from typing import List
from abc import ABC, abstractmethod
import asyncio


class Embeddings(ABC):

    @abstractmethod
    def embed_batch(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Embed text batch."""

    def embed(self, text: str, **kwargs) -> List[float]:
        """Embed text."""
        return self.embed_batch(texts=[text], **kwargs)[0]

    async def aembed(self, text: str, **kwargs) -> List[float]:
        """Asynchronous Embed text."""
        return await asyncio.get_running_loop().run_in_executor(
            None, self.embed, text, **kwargs
        )

    async def aembed_batch(self, texts: [str], **kwargs) -> List[List[float]]:
        """Asynchronous Embed text."""
        return await asyncio.get_running_loop().run_in_executor(
            None, self.embed_batch, texts, **kwargs
        )
