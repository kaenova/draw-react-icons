import typing
import numpy as np

from PIL import Image


class IconData:
    def __init__(
        self,
        parent_name: "str",
        icon_name: "str",
        img_path: "str",
        invert_image=False,
        normalize_pixels=True,
    ) -> None:
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
        self.numpy = img

    def to_numpy(self) -> "np.ndarray":
        return self.numpy

    def to_pillow(self) -> "Image":  # type: ignore
        return Image.fromarray(np.uint8(self.numpy * 255), "L")  # type: ignore
