from abc import ABC, abstractmethod
from .icon_data import *
from .type import ArrayNxNx1

class Embedder(ABC):
    @abstractmethod
    def embeds(self, icon_data: ArrayNxNx1) -> list:
        pass

    @abstractmethod
    def name(self) -> "str":
        pass

    @abstractmethod
    def num_dimensions(self) -> "int":
        pass
