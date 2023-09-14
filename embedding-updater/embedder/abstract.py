from abc import ABC, abstractmethod
from core import IconData


class Embedder(ABC):
    @abstractmethod
    def embeds(self, icon_data: IconData):
        pass

    @abstractmethod
    def name(self) -> "str":
        pass
