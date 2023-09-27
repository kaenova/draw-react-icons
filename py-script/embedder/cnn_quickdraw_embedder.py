import core
import cv2

import numpy as np
import onnxruntime as ort

from huggingface_hub import hf_hub_download


class CNNQuickDraw(core.Embedder):
    repo_id = "kaenova/draw-react-icons"
    filename = "quick_draw_embed_500000_input_64_64_1.onnx"

    input_shape_size = (1, 64, 64, 1)
    input_name = "x"
    output_name = "dense"

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
        )  # [64, 64]
        data = np.expand_dims(data, -1)  # [64, 64, 1]
        data = np.expand_dims(data, 0)  # [1, 64, 64, 1]
        results_ort: np.ndarray = self.session.run(
            [self.output_name], {self.input_name: data}
        )[0]
        final: list[float] = results_ort.flatten().tolist()
        return final

    @staticmethod
    def name() -> str:
        return "CNNQuickDraw"

    def num_dimensions(self) -> int:
        input1 = np.zeros(self.input_shape_size, np.float32)
        results_ort: np.ndarray = self.session.run(
            [self.output_name], {self.input_name: input1}
        )[0]
        final: list[float] = results_ort.flatten().tolist()
        return len(final)
