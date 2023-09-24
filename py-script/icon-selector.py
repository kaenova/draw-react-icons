from dotenv import load_dotenv

load_dotenv()

import utils
import timeit
import typing
import repository

from core import log
from constants import *

if "__main__" == __name__:
    arg = utils.parse_arg_icon_selector(
        DEFAULT_ZIP_PATH,
        DEFAULT_JSON_PATH,
    )

    log.info("starting script 🔥")
    log.info(
        f"Detected Input arg: {arg.__dict__}",
    )

    # Initialize Repository
    log.info("Initializing Repository 📚")
    repository = repository.ApplicationRepository(
        arg.qdrant_endpoint, arg.qdrant_api_key
    )
    checksum_collection_name = repository.get_checksum_collection_name()
    checksum_collection = repository.collection_exists(checksum_collection_name)
    if checksum_collection is None:
        log.info(
            f"Checksum Collection not exist, creating collection of {checksum_collection_name}"
        )
        checksum_collection = repository.craete_new_checksum_collection()
        log.info("Checksum Collection created")
    log.info("Repository initialize")

    # Unzip data
    log.info("Extracting zip 📦")
    t = timeit.default_timer()
    utils.extract_zip(arg.i, OUTPUT_ZIP_FOLDER_PATH)
    t_end = timeit.default_timer()
    log.debug(f"Zip extractor {t_end - t}")
    log.info("Zip extracted")

    # Get checksum from each parent icon data
    log.info("Getting checksum on folder's icon")
    t = timeit.default_timer()
    hash_stats = utils.get_folder_checksum_stat(OUTPUT_ZIP_FOLDER_PATH)
    t_end = timeit.default_timer()
    log.debug(f"Checksum {t_end - t}")
    log.info(f"Folder checksum stats: {hash_stats}")

    # check mismatch checksum folder
    log.info("Checking mismatch checksum")
    mismatch_checksum_parent_id: "typing.Dict[str, str]" = {}
    for parent_id in hash_stats:
        checksum = repository.get_checksum_parent_icon(
            parent_id,
        )
        if checksum is None or checksum != hash_stats[parent_id]:
            mismatch_checksum_parent_id[parent_id] = hash_stats[parent_id]
    log.info("Mismatch checksum generated")

    utils.generate_json_checksum(mismatch_checksum_parent_id, arg.o)
    log.info(f"script finished, and output a json on {arg.o}")
