import typing
from dataclasses import dataclass
import numpy as np
from PIL import Image
import os
import mimetypes
import logging


@dataclass
class ParentFolderHash:
    parent_id: "str"
    hash_str: "str"


@dataclass
class SmartUpdateOutput:
    update_parent_id_folders: "typing.List[str]"
    renew_all_collection: "bool"


class IconData:
    def __init__(
        self,
        icon_id: "str",
        img_path: "str",
        resize_shape=(28, 28),
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

        self.icon_id = icon_id
        self.img_path = img_path
        self.shape = resize_shape
        self.numpy = img

    def to_numpy(self) -> "np.ndarray":
        return self.numpy

    def to_pillow(self) -> "Image":
        img_np = np.reshape(self.numpy, self.shape)
        return Image.fromarray(np.uint8(img_np * 255), "L")


class ParentIconData:
    def __init__(
        self,
        parent_id: "str",
        parent_path: "str",
        resize_shape=(28, 28),
        invert_image=False,
        normalize_pixels=True,
    ) -> None:
        self.parent_id = parent_id
        self.parent_path = parent_path

        self.icon_data: "typing.List[IconData]" = []
        image_list = os.listdir(parent_path)

        for image_filename in image_list:
            image_path = os.path.join(parent_path, image_filename)
            mime = mimetypes.guess_type(image_path)
            if mime[0] not in ["image/jpg", "image/jpeg"]:
                continue
            try:
                self.icon_data.append(
                    IconData(
                        image_filename.split(".")[0],
                        image_path,
                        resize_shape,
                        invert_image,
                        normalize_pixels,
                    )
                )
            except:
                logging.info(f"Cannot load {image_path}, file may be corrupted")


if __name__ == "__main__":
    icon = IconData(
        "a",
        "b",
        "dist/ai/AiFillAccountBook.jpg",
        resize_shape=(128, 128),
        invert_image=False,
    )
    icon.to_pillow().show()
