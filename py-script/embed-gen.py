# NOTE: If you wnat to develop this, make sure you have dist.zip inside embedding-updater folder
# Download the dist.zip through here: https://drive.google.com/file/d/13Fnm3ingRAmDnhu2P8p8wROBfhbD7QwL/view?usp=sharing

from dotenv import load_dotenv

load_dotenv()

import os
import core
import time
import utils
import timeit
import typing
import repository

from core import log
from constants import *


if "__main__" == __name__:
    arg = utils.parse_arg_embed_generator(
        DEFAULT_ZIP_PATH,
        DEFAULT_JSON_PATH,
        EMBEDDER_DICT,
        repository.QDRANT_INDEX_METHOD_OPTS,
    )
    arg.indexing = repository.QDRANT_INDEX_METHOD[arg.indexing]

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
        arg.qdrant_endpoint, arg.qdrant_api_key
    )

    # Prepare collection
    log.info("Checking collection")
    collection_info = core.CollectionInformation(
        embedder_name=embedder.name(),
        index=arg.indexing,
    )
    checksum_collection_name = repository.get_checksum_collection_name()
    # Check if all collection exist
    embeddings_collection = repository.collection_exists(collection_info.full_name)
    checksum_collection = repository.collection_exists(checksum_collection_name)
    if embeddings_collection is None:
        log.info(
            f"Embedding Collection not exist, creating collection of {collection_info.full_name} with {arg.indexing} indexing"
        )
        embeddings_collection = repository.create_new_embedding_collection(
            embedder,
            arg.indexing,
        )
        log.info("Embedding Collection created")
    if checksum_collection is None:
        log.info(
            f"Checksum Collection not exist, creating collection of {checksum_collection_name}"
        )
        checksum_collection = repository.craete_new_checksum_collection()
        log.info("Checksum Collection created")
    log.info("Collection checked")
    log.info("Repository initialize")

    # Unzip data
    log.info("Extracting zip 📦")
    t = timeit.default_timer()
    utils.extract_zip(arg.input_zip, OUTPUT_ZIP_FOLDER_PATH)
    t_end = timeit.default_timer()
    log.debug(f"Zip extractor {t_end - t}")
    log.info("Zip extracted")

    # Load Json Checksum data
    log.info("Load checksum json data 📦")
    t = timeit.default_timer()
    checksums_data = utils.read_json_checksum(arg.input_json)
    t_end = timeit.default_timer()
    log.debug(f"Checksum loader {t_end - t}")
    log.info("JSON Checksum loaded")

    # Load Checksum Database
    log.info("Load checksum database 📦")
    checksums_data_db = repository.get_checksum(embedder, arg.indexing)
    log.info("Database Checksum loaded 📦")

    # Check mismatch checksum
    log.info("Checking mismatch checksum")
    mismatch_checksum_parent_id = []
    if checksums_data_db is None:
        mismatch_checksum_parent_id = list(checksums_data.keys())
    else:
        for parent_id in checksums_data:
            if (parent_id not in checksums_data_db) or (
                checksums_data[parent_id] != checksums_data_db[parent_id]
            ):
                mismatch_checksum_parent_id.append(parent_id)
    log.info(f"Mismatch checksum parent: {mismatch_checksum_parent_id}")

    # Prepare icon data to be uploaded
    log.info(f"Loading Data of a  mismatch checksum")
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

    # Disable indexing
    log.info("Disabling indexing")
    repository.disable_indexing(embedder, arg.indexing)
    log.info("Indexing disabled")

    # Save to Embedding DB
    log.info("Saving unmatch checksum embedding to database")
    total_icon_uploaded = 0
    all_upload_icons: typing.List[core.IconEmbeddings] = []
    for parent_icon_data in embed_parent_icon_data:
        for icon in parent_icon_data.icon_data_embeddings:
            all_upload_icons.append(icon)
    log.info(f"Total Icon: {len(all_upload_icons)}")
    for icon_batch, i in utils.batch(all_upload_icons, arg.upload_batch):
        t = timeit.default_timer()
        repository.add_or_update_icon(
            embedder,
            arg.indexing,
            icon_batch,
        )
        total_icon_uploaded += len(icon_batch)
        log.info(f"Uploaded {total_icon_uploaded} / {len(all_upload_icons)} icons")
        t_end = timeit.default_timer()
        log.debug(f"Embedding save {t_end - t}")
    log.info("Unmatch Embedding saved")

    # Enable indexing
    log.info("Enable indexing")
    repository.enable_indexing(embedder, arg.indexing)
    log.info("Indexing enabled")

    # Wait until indexing finished
    log.info("Waiting for collection status to be ready")
    collection_status_ready = False
    while not collection_status_ready:
        time.sleep(5)
        collection_status_ready = repository.collection_is_ready(
            embedder,
            arg.indexing,
        )
    log.info("Collection ready")

    # Save checksum
    log.info("Saving checksum to database")
    t = timeit.default_timer()
    repository.add_or_update_checksum(embedder, arg.indexing, checksums_data)
    t_end = timeit.default_timer()
    log.debug(f"Embedding save {t_end - t}")
    log.info("Unmatch Embedding saved")

    exit(0)
