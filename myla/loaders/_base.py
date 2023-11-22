from abc import ABC, abstractmethod

class Loader(ABC):

    @abstractmethod
    def load(file):
        """Load data from a file"""