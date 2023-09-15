# NOTE: If you wnat to develop this, make sure you have dist.zip inside embedding-updater folder
# Download the dist.zip through here: https://drive.google.com/file/d/13Fnm3ingRAmDnhu2P8p8wROBfhbD7QwL/view?usp=sharing

import os
import pathlib
import utils
import argparse
import embedder
import core
import timeit
import typing
import repository
from logger import log


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
arg_parser.add_argument(
    "--mysql-endpoint",
    default="mysql+mysqldb://root:changeme@localhost:3306/draw-react-icons",
    help="Weaviate Endpoint to read and save data",
)


if "__main__" == __name__:
    arg = arg_parser.parse_args()
    log.info(
        f"Detected Input arg: {arg.__dict__}",
    )

    log.info("starting script 🔥")

    # Initialize Repository
    log.info("Initializing Repository 📚")
    repository = repository.ApplicationRepository(
        arg.weaviate_endpoint, arg.mysql_endpoint
    )
    log.info("Repository initialize")

    # Initialize embedder
    embedder = EMBEDDER_DICT[arg.embedder]()

    # log.info("Extracting zip 📦")
    # t = timeit.default_timer()
    # utils.extract_zip(arg.i, OUTPUT_ZIP_FOLDER_PATH)
    # t_end = timeit.default_timer()
    # log.debug(f"Zip extractor {t_end - t}")
    # log.info("Zip extracted")

    log.info("Getting checksum on folder's icon")
    t = timeit.default_timer()
    hash_stats = utils.get_folder_checksum_stat(OUTPUT_ZIP_FOLDER_PATH)
    t_end = timeit.default_timer()
    log.debug(f"Checksum {t_end - t}")
    log.info(f"Folder checksum stats: {hash_stats}")

    # check mismatch checksum
    mismatch_checksum_parent_id: "typing.List[str]" = []
    for parent_id in hash_stats:
        checksum = repository.get_checksum_parent_icon(parent_id)
        if checksum is None or checksum != hash_stats[parent_id]:
            mismatch_checksum_parent_id.append(parent_id)

    # Prepare Data to be embeded from the mismatch checksum
    t = timeit.default_timer()
    log.info(f"Loading Data from a mismatch checksum: {mismatch_checksum_parent_id}")
    embed_parent_icon_data: "typing.List[core.ParentIconData]" = []
    for parent_id in mismatch_checksum_parent_id:
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
    log.debug(f"Data Loader {t_end - t}")

    # # TODO: Create icon embedding based on icon to be saved into database, use the filename of the icon as key
    # embedder.embeds(embed_parent_icon_data[0].icon_data[0])

    # Save All Checksum on the mismatch checksum
    log.info("Saving new checksum on database 📦")
    t = timeit.default_timer()
    for parent_id in mismatch_checksum_parent_id:
        repository.add_or_update_icon_checksum(parent_id, hash_stats[parent_id])
    t_end = timeit.default_timer()
    log.debug(f"Checksum saver {t_end - t}")
    log.info("New checksum saved 📦")

    exit(0)
