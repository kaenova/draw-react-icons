# NOTE: If you wnat to develop this, make sure you have dist.zip inside embedding-updater folder
# Download the dist.zip through here: https://drive.google.com/file/d/13Fnm3ingRAmDnhu2P8p8wROBfhbD7QwL/view?usp=sharing

import os
import pathlib
import utils
import argparse
import embedder
import core
import timeit
import logging
import weaviate

logging.root.setLevel(logging.NOTSET)

logging.info("starting script 🔥")

# Zip Input
script_path = pathlib.Path(__file__).parent.resolve()
OUTPUT_ZIP_FOLDER_PATH = os.path.join(script_path, "dist")
DEFAULT_ZIP_PATH = os.path.join(script_path, "dist.zip")

# Embedder
EMBEDDER_DICT = {"pixel": embedder.pixel_embedder.PixelEmbedder}

arg_parser = argparse.ArgumentParser(
    "Embedding Updater",
    "This program is a runner to run an embedding inference for an react-icons image that are bundled in a zip file",
)
arg_parser.add_argument("-i", default=DEFAULT_ZIP_PATH, help="Path of input zip file")
arg_parser.add_argument(
    "--embedder",
    choices=list(EMBEDDER_DICT.keys()),
    default=list(EMBEDDER_DICT.keys())[0],
    help="Embedder model to embed the image",
)
arg_parser.add_argument(
    "--weaviate-endpoint",
    default="http://localhost:8080",
    help="Weaviate Endpoint to read and save data",
)
arg = arg_parser.parse_args()
logging.info(
    f"Detected Input arg: {arg.__dict__}",
)

weaviate_client = weaviate.Client(arg.weaviate_endpoint)
weaviate_client.schema.get()

# Initialize embedder
embedder = EMBEDDER_DICT[arg.embedder]()

logging.info("Extracting zip 📦")
t = timeit.default_timer()
utils.extract_zip(arg.i, OUTPUT_ZIP_FOLDER_PATH)
t_end = timeit.default_timer()
logging.debug(f"Zip extractor {t_end - t}")
logging.info("Zip extracted")

logging.info("Getting checksum on folder's icon")
t = timeit.default_timer()
hash_stats = utils.get_folder_checksum_stat(OUTPUT_ZIP_FOLDER_PATH)
t_end = timeit.default_timer()
logging.debug(f"Checksum {t_end - t}")
logging.info(f"Folder checksum stats: {hash_stats}")

# TODO: Get checksum data stored in database if available

# TODO: Compare hash_stats and checksum data on database, list if the parent_id is not present or the checksum does not match. The code below is dummy that consider all parent icon
embed_parent_id = os.listdir(OUTPUT_ZIP_FOLDER_PATH)

# Prepare Data to be embeded
t = timeit.default_timer()
embed_parent_icon_data = []
for parent_id in embed_parent_id:
    embed_parent_icon_data.append(
        core.ParentIconData(
            parent_id=parent_id,
            parent_path=os.path.join(OUTPUT_ZIP_FOLDER_PATH, parent_id),
            invert_image=False,
            normalize_pixels=True,
            resize_shape=(28, 28),
        )
    )
t_end = timeit.default_timer()
logging.debug(f"Data Loader {t_end - t}")

# TODO: Create icon embedding based on icon to be saved into database, use the filename of the icon as key

exit(0)
