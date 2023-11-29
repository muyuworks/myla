from abc import ABC, abstractmethod
from typing import Iterator
from ._base import Record


class Loader(ABC):

    @abstractmethod
    def load(self, file) -> Iterator[Record]:
        """Load data from a file"""
