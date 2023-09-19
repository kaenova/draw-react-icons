from abc import ABC, abstractmethod
from .icon_data import *

import numpy as np


class Embedder(ABC):
    @abstractmethod
    def embeds(self, icon_data: np.ndarray) -> list:
        pass

    @abstractmethod
    def name(self) -> "str":
        pass

    @abstractmethod
    def num_dimensions(self) -> "int":
        pass
