import os
import pathlib

import embedder

# Default ZIP input
script_path = pathlib.Path(__file__).parent.resolve()
OUTPUT_ZIP_FOLDER_PATH = os.path.join(script_path, "dist")
DEFAULT_ZIP_PATH = os.path.join(script_path, "dist.zip")
DEFAULT_JSON_PATH = os.path.join(script_path, "checksum.json")

# Embedder
EMBEDDER_DICT = {
    embedder.pixel_embedder.PixelEmbedder.name(): embedder.pixel_embedder.PixelEmbedder
}
