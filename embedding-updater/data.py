import numpy as np
import tensorflow as tf
import PIL


class IconData:
    def __init__(
        self,
        parent_id: "str",
        icon_id: "str",
        img_path: "str",
        resize_shape=(28, 28),
        invert_image=False,
    ) -> None:
        assert len(resize_shape) == 2

        # Get image
        img = PIL.Image.open(img_path)
        img = img.convert("L")

        # Process image
        img = np.expand_dims(np.array(img), -1)
        img = tf.image.resize(img, resize_shape[:2], antialias=True)
        img = img / 255

        if invert_image:
            img = (img - 1) * -1

        self.parent_id = parent_id
        self.icon_id = icon_id
        self.img_path = img_path
        self.shape = resize_shape
        self.tensor_img = img

    def to_tensor(self):
        return self.tensor_img

    def to_numpy(self):
        return self.tensor_img.numpy()

    def to_pillow(self) -> "PIL.Image":
        img_np = self.to_numpy()
        img_np = np.reshape(img_np, self.shape)
        return PIL.Image.fromarray(np.uint8(img_np * 255), "L")

    def to_embeddings(self, model: tf.keras.Model) -> "np.ndarray":
        model_input_shape = model.input.type_spec.shape[1:-1]  # (H, W)
        assert model_input_shape == self.shape
        prediction = model.predict(tf.expand_dims(self.tensor_img, 0), verbose=0)
        return prediction[0]


class IconDataEmbeddings:
    def __init__(
        self,
        icon: IconData,
    ) -> None:
        self.icon = icon

        pass


if __name__ == "__main__":
    icon = IconData(
        "a",
        "b",
        "dist/ai/AiFillAccountBook.jpg",
        resize_shape=(128, 128),
        invert_image=False,
    )
    icon.to_pillow().show()
