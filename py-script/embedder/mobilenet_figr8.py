import core
import cv2

import numpy as np
import onnxruntime as ort

from huggingface_hub import hf_hub_download


class MobileNetFigr8(core.Embedder):
    repo_id = "kaenova/draw-react-icons"
    filename = "mobilenet-custom_fig-8_input_1000_20_80_80_1_embed_100epoch.onnx"

    input_shape_size = (1, 80, 80, 1)
    input_name = "x"
    output_name = "flatten"

    def __init__(self) -> None:
        super().__init__()
        model_path = hf_hub_download(repo_id=self.repo_id, filename=self.filename)
        self.session = ort.InferenceSession(
            model_path, providers=["CPUExecutionProvider"]
        )

    def embeds(self, icon_data: core.embedder.ArrayNxNx1) -> list:
        icon_data = np.squeeze(icon_data, -1)  # [H,W]
        data = cv2.resize(
            icon_data,
            self.input_shape_size[1:3],
        )  # [80, 80]
        data = np.expand_dims(data, -1)  # [80, 80, 1]
        data = np.expand_dims(data, 0)  # [1, 80, 80, 1]
        results_ort: np.ndarray = self.session.run(
            [self.output_name], {self.input_name: data}
        )[0]
        final: list[float] = results_ort.flatten().tolist()
        return final

    @staticmethod
    def name() -> str:
        return "MobileNetFigr8"

    def num_dimensions(self) -> int:
        input1 = np.zeros(self.input_shape_size, np.float32)
        results_ort: np.ndarray = self.session.run(
            [self.output_name], {self.input_name: input1}
        )[0]
        final: list[float] = results_ort.flatten().tolist()
        return len(final)
