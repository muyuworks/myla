import pandas as pd
from typing import Iterator
from ._base import Record
from .loaders import Loader

class PandasLoader(Loader):
    def load(self, file) -> Iterator[Record]:
        df = pd.read_csv(file)

        for _, r in df.iterrows():
            yield r.to_dict()