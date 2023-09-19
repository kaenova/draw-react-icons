# NOTE: If you wnat to develop this, make sure you have dist.zip inside embedding-updater folder
# Download the dist.zip through here: https://drive.google.com/file/d/13Fnm3ingRAmDnhu2P8p8wROBfhbD7QwL/view?usp=sharing

import os
import core
import utils
import timeit
import typing
import pathlib
import embedder
import repository

from core import log

# Default ZIP input
script_path = pathlib.Path(__file__).parent.resolve()
OUTPUT_ZIP_FOLDER_PATH = os.path.join(script_path, "dist")
DEFAULT_ZIP_PATH = os.path.join(script_path, "dist.zip")

# Embedder
EMBEDDER_DICT = {"pixel": embedder.pixel_embedder.PixelEmbedder}


if "__main__" == __name__:
    arg = utils.parse_arg(
        DEFAULT_ZIP_PATH,
        EMBEDDER_DICT,
        repository.MILVUS_INDEX_METHOD_OPTS,
    )

    log.info("starting script 🔥")
    log.info(
        f"Detected Input arg: {arg.__dict__}",
    )

    # Initialize embedder
    log.info("Initializing Embedder")
    embedder = EMBEDDER_DICT[arg.embedder]()
    log.info("Embedder Initialized")

    # Initialize Repository
    log.info("Initializing Repository 📚")
    repository = repository.ApplicationRepository(
        arg.milvus_endpoint,
        arg.milvus_api_key,
        arg.milvus_db,
        embedder,
        arg.milvus_indexing,
    )
    log.info("Repository initialize")

    # Unzip data
    log.info("Extracting zip 📦")
    t = timeit.default_timer()
    utils.extract_zip(arg.i, OUTPUT_ZIP_FOLDER_PATH)
    t_end = timeit.default_timer()
    log.debug(f"Zip extractor {t_end - t}")
    log.info("Zip extracted")

    # Count data
    log.info("Getting the number on folder's icon")
    t = timeit.default_timer()
    count_stats = utils.get_folder_count_stat(OUTPUT_ZIP_FOLDER_PATH)
    t_end = timeit.default_timer()
    log.info(f"Folder count stats: {count_stats}")

    # Get checksum from each parent icon data
    log.info("Getting checksum on folder's icon")
    t = timeit.default_timer()
    hash_stats = utils.get_folder_checksum_stat(OUTPUT_ZIP_FOLDER_PATH)
    t_end = timeit.default_timer()
    log.debug(f"Checksum {t_end - t}")
    log.info(f"Folder checksum stats: {hash_stats}")

    # check mismatch checksum folder
    mismatch_checksum_parent_id: "typing.List[str]" = []
    for parent_id in hash_stats:
        checksum = repository.get_checksum_parent_icon(
            parent_id,
        )
        if checksum is None or checksum != hash_stats[parent_id]:
            mismatch_checksum_parent_id.append(parent_id)

    # Prepare icon data to be uploaded
    log.info(f"Loading Data from a mismatch checksum: {mismatch_checksum_parent_id}")
    t = timeit.default_timer()
    embed_parent_icon_data: "typing.List[core.ParentIconData]" = []
    for parent_id in mismatch_checksum_parent_id:
        embed_parent_icon_data.append(
            core.ParentIconData(
                parent_id=parent_id,
                parent_path=os.path.join(OUTPUT_ZIP_FOLDER_PATH, parent_id),
                invert_image=arg.invert,
                normalize_pixels=arg.normalize,
                embedder=embedder,
            )
        )
    t_end = timeit.default_timer()
    log.debug(f"Data Loader {t_end - t}")
    log.info(f"Data Loaded")

    # Save to Embedding DB
    log.info("Saving unmatch checksum embedding to database")
    t = timeit.default_timer()
    for embed_parent_data in embed_parent_icon_data:
        for icon_embed_batch in utils.batch(
            embed_parent_data.icon_data_embeddings,
            arg.milvus_upload_batch,
        ):
            repository.add_or_update_icon(
                icon_embed_batch,
            )
    t_end = timeit.default_timer()
    log.debug(f"Embedding save {t_end - t}")
    log.info("Unmatch Embedding saved")

    # Save All Checksum on the mismatch checksum
    log.info("Saving new checksum on database 📦")
    t = timeit.default_timer()
    for parent_id in mismatch_checksum_parent_id:
        repository.add_or_update_icon_checksum(
            parent_id,
            hash_stats[parent_id],
        )
    t_end = timeit.default_timer()
    log.debug(f"Checksum saver {t_end - t}")
    log.info("New checksum saved 📦")

    exit(0)
