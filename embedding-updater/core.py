import os
import typing
import mimetypes
import logging

import numpy as np

from PIL import Image
from abc import ABC, abstractmethod
from dataclasses import dataclass
from logger import log


class IconData:
    def __init__(
        self,
        parent_name: "str",
        icon_name: "str",
        img_path: "str",
        resize_shape: "typing.Tuple[int, int]" = (28, 28),
        invert_image=False,
        normalize_pixels=True,
    ) -> None:
        assert len(resize_shape) == 2

        # Get image
        img = Image.open(img_path)
        img = img.convert("L")  # Single channel image (BnW)

        # Process image
        img = np.expand_dims(np.array(img), -1)  # [H, W, 1]
        if normalize_pixels:
            img = img / 255

        if invert_image:
            img = (img - 1) * -1

        self.parent_name = parent_name
        self.icon_name = icon_name
        self.img_path = img_path
        self.shape = resize_shape
        self.numpy = img

    def to_numpy(self) -> "np.ndarray":
        return self.numpy

    def to_pillow(self) -> "Image":  # type: ignore
        img_np = np.reshape(self.numpy, self.shape)
        return Image.fromarray(np.uint8(img_np * 255), "L")  # type: ignore


class ParentIconData:
    def __init__(
        self,
        parent_id: "str",
        parent_path: "str",
        embedder: "Embedder",
        resize_shape=(28, 28),
        invert_image=False,
        normalize_pixels=True,
    ) -> None:
        self.parent_id = parent_id
        self.parent_path = parent_path

        self.icon_data_embeddings: "typing.List[IconEmbeddings]" = []
        self.embedder = embedder
        image_list = os.listdir(parent_path)

        for image_filename in image_list:
            image_path = os.path.join(parent_path, image_filename)
            mime = mimetypes.guess_type(image_path)

            if mime[0] not in ["image/jpg", "image/jpeg"]:
                log.warn(f"{image_path} doesn't have the right mime type")
                continue

            icon_name = image_filename.split(".")[0]
            parent_name = parent_id

            # Try to load the data
            try:
                icon = IconData(
                    parent_name,
                    icon_name,
                    image_path,
                    resize_shape,
                    invert_image,
                    normalize_pixels,
                )
            except:
                log.warn(f"Cannot load {image_path}, file may be corrupted")
                continue

            icon_embeddings = self.embedder.embeds(icon)

            self.icon_data_embeddings.append(
                IconEmbeddings(
                    icon_data=icon,
                    embeddings=icon_embeddings,
                )
            )


@dataclass
class IconEmbeddings:
    icon_data: "IconData"
    embeddings: list


class Embedder(ABC):
    @abstractmethod
    def embeds(self, icon_data: IconData) -> list:
        pass

    @abstractmethod
    def name(self) -> "str":
        pass

    @abstractmethod
    def num_dimensions(self) -> "int":
        pass


if __name__ == "__main__":
    icon = IconData(
        "a",
        "b",
        "dist/ai/AiFillAccountBook.jpg",
        (128, 128),
        False,
    )
