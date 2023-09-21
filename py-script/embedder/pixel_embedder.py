import core
import numpy as np
import cv2


class PixelEmbedder(core.Embedder):
    shape_size = (28, 28)

    def __init__(self) -> None:
        super().__init__()

    def embeds(self, icon: np.ndarray) -> list:
        data = icon
        data = cv2.resize(
            data,
            self.shape_size,
        )
        return data.flatten().tolist()

    @staticmethod
    def name() -> str:
        return "PixelEmbedder"

    def num_dimensions(self) -> int:
        return self.shape_size[0] * self.shape_size[1]
