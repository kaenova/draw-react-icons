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


# Default ZIP input
script_path = pathlib.Path(__file__).parent.resolve()
OUTPUT_ZIP_FOLDER_PATH = os.path.join(script_path, "dist")
DEFAULT_ZIP_PATH = os.path.join(script_path, "dist.zip")

# Embedder
EMBEDDER_DICT = {"pixel": embedder.PixelEmbedder}

arg_parser = argparse.ArgumentParser(
    "Embedding Updater",
    "This program is a runner to run an embedding inference for an react-icons image that are bundled in a zip file. The image of the emdeds need to have a background of black and the foreground of white. You can invert the image using --invert argument",
)
arg_parser.add_argument(
    "-i",
    default=DEFAULT_ZIP_PATH,
    help="Path of input zip file",
)
arg_parser.add_argument(
    "--embedder",
    choices=list(EMBEDDER_DICT.keys()),
    default=list(EMBEDDER_DICT.keys())[0],
    help="Embedder model to embed the image",
)
arg_parser.add_argument(
    "--invert",
    help="Invert image black and white",
    type=bool,
    default=False,
)
arg_parser.add_argument(
    "--normalize",
    help="True image to [0..1] range",
    type=bool,
    default=True,
)
arg_parser.add_argument(
    "--milvus-indexing",
    choices=repository.MILVUS_INDEX_METHOD_OPTS,
    default=repository.MILVUS_INDEX_METHOD_OPTS[0],
    help="Indexing method on milvus if collection is not created",
)
arg_parser.add_argument(
    "--milvus-endpoint",
    help="Milvus zilliz endpoint URI",
    required=True,
)
arg_parser.add_argument(
    "--milvus-api-key",
    help="Milvus zilliz API Key",
    required=True,
)
arg_parser.add_argument(
    "--milvus-db",
    help="Milvus Database",
    required=True,
)
arg_parser.add_argument(
    "--milvus-upload-batch",
    help="Milvus number of batch to be uploaded, for rough estimation there are 44000 icons",
    type=int,
    default=2000,
)


if "__main__" == __name__:
    arg = arg_parser.parse_args()

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
    )
    log.info("Repository initialize")

    # Prepare Milvus collection
    log.info("Checking collection name on repository")
    embedding_collection_name = repository.get_embedding_collection_name(
        embedder, arg.milvus_indexing
    )
    checksum_collection_name = repository.get_checksum_collection_name()

    # Check if all collection exist
    embeddings_collection = repository.collection_exists(embedding_collection_name)
    checksum_collection = repository.collection_exists(checksum_collection_name)
    if embeddings_collection is None:
        log.info(
            f"Embedding Collection not exist, creating collection of {embedding_collection_name} with {arg.milvus_indexing} indexing"
        )
        embeddings_collection = repository.create_new_embedding_collection(
            embedder,
            arg.milvus_indexing,
        )
        log.info("Embedding Collection created")

    if checksum_collection is None:
        log.info(
            f"Checksum Collection not exist, creating collection of {checksum_collection_name}"
        )
        checksum_collection = repository.craete_new_checksum_collection()
        log.info("Checksum Collection created")

    # Check if all collection loaded
    if not repository.collection_is_loaded(embeddings_collection):
        log.info("Embeddings Collection is not loadded, loading the collection")
        repository.load_collection(embeddings_collection)
        log.info("Embeddings Collection loaded")
    if not repository.collection_is_loaded(checksum_collection):
        log.info("Checksum Collection is not loadded, loading the collection")
        repository.load_collection(checksum_collection)
        log.info("Checksum Collection loaded")

    log.info("Collection checked")

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
            checksum_collection,
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
                resize_shape=(28, 28),
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
                embeddings_collection,
            )
    t_end = timeit.default_timer()
    log.debug(f"Embedding save {t_end - t}")
    log.info("Unmatch Embedding saved")

    # Save All Checksum on the mismatch checksum
    log.info("Saving new checksum on database 📦")
    t = timeit.default_timer()
    for parent_id in mismatch_checksum_parent_id:
        repository.add_or_update_icon_checksum(
            checksum_collection, parent_id, hash_stats[parent_id]
        )
    t_end = timeit.default_timer()
    log.debug(f"Checksum saver {t_end - t}")
    log.info("New checksum saved 📦")

    exit(0)
