from typing import List
from abc import ABC, abstractmethod
import asyncio


class Embeddings(ABC):

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed text batch."""

    def embed(self, text: str) -> List[float]:
        """Embed text."""
        return self.embed_batch(texts=[text])[0]

    async def aembed(self, text: str) -> List[float]:
        """Asynchronous Embed text."""
        return await asyncio.get_running_loop().run_in_executor(
            None, self.embed, text
        )

    async def aembed_batch(self, texts: [str]) -> List[List[float]]:
        """Asynchronous Embed text."""
        return await asyncio.get_running_loop().run_in_executor(
            None, self.embed_batch, texts
        )