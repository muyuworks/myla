from abc import ABC, abstractmethod
from typing import Iterator, Optional, Dict
from ._base import Record


class Loader(ABC):

    @abstractmethod
    def load(self, file, metadata: Optional[Dict] = None) -> Iterator[Record]:
        """Load data from a file"""
