import core
import numpy as np
import tensorflow as tf


class PixelEmbedder(core.Embedder):
    shape_size = (28, 28)

    def __init__(self) -> None:
        super().__init__()

    def embeds(self, icon: np.ndarray) -> list:
        data = icon
        data = tf.image.resize(
            data,
            self.shape_size,
            antialias=True,
        )
        return data.numpy().flatten().tolist()

    def name(self) -> str:
        return self.__class__.__name__

    def num_dimensions(self) -> int:
        return self.shape_size[0] * self.shape_size[1]
