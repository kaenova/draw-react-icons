from .embedder import Embedder
from .data_class import IconEmbeddings
from .logger import log
from .icon_data import IconData

import mimetypes
import typing
import os


class ParentIconData:
    def __init__(
        self,
        parent_id: "str",
        parent_path: "str",
        embedder: Embedder,
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
                    invert_image,
                    normalize_pixels,
                )
            except:
                log.warn(f"Cannot load {image_path}, file may be corrupted")
                continue

            icon_embeddings = self.embedder.embeds(icon.numpy)

            self.icon_data_embeddings.append(
                IconEmbeddings(
                    icon_data=icon,
                    embeddings=icon_embeddings,
                )
            )
