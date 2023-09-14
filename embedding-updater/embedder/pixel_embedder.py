from .abstract import Embedder
from core import IconData


class PixelEmbedder(Embedder):
    def __init__(self) -> None:
        super().__init__()

    def embeds(self, icon_data: "IconData"):
        return icon_data.to_numpy().flatten()

    def name(self) -> str:
        return self.__class__.__name__
