import pandas as pd
from typing import Iterator
from ._base import Record
from .loaders import Loader

class PandasLoader(Loader):
    def __init__(self, ftype) -> None:
        super().__init__()
        self._ftype = ftype

    def load(self, file) -> Iterator[Record]:
        if self._ftype == 'csv':
            df = pd.read_csv(file)
        elif self._ftype == 'xls' or self._ftype == 'xlsx':
            df = pd.read_excel(file)
        elif self._ftype == 'json':
            df = pd.read_json(file)
        else:
            raise ValueError(f"File type not supported: {self._ftype}")

        for _, r in df.iterrows():
            yield r.to_dict()