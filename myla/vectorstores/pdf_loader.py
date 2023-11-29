import math
from typing import Iterator
from myla.vectorstores._base import Record
from .loaders import Loader


class PDFLoader(Loader):
    def __init__(self, chunk_size=500, chunk_overlap=50) -> None:
        super().__init__()
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def load(self, file) -> Iterator[Record]:
        try:
            import pypdf
        except ImportError as e:
            raise (
                "Could not import pypdf python package. "
                "Please install it with `pip install pypdf`."
            ) from e
        reader = pypdf.PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            for s in self._split(text=text):
                yield {"text": s}

    def _split(self, text):
        for i in range(math.ceil(len(text)/self._chunk_size)):
            begin = i * self._chunk_size
            end = begin + self._chunk_size

            if i > 0:
                begin -= self._chunk_overlap
            if begin < 0:
                begin = 0
            if end > len(text):
                end = len(text)

            yield text[begin: end]
