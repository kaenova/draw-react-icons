from dotenv import load_dotenv

load_dotenv()

import utils
import timeit
import repository

from core import log
from constants import *

if "__main__" == __name__:
    arg = utils.parse_arg_update_checksum(
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
        raise RuntimeError("Checksum collection is not exist")
    log.info("Repository initialize")

    # Load Json Checksum data
    log.info("Load checksum json data 📦")
    t = timeit.default_timer()
    checksums_data = utils.read_json_checksum(arg.i)
    t_end = timeit.default_timer()
    log.debug(f"Checksum loader {t_end - t}")
    log.info(f"JSON Checksum loaded with data {checksums_data}")

    # Save All Checksum on the mismatch checksum
    log.info("Saving new checksum on database 📦")
    t = timeit.default_timer()
    for parent_id in checksums_data:
        repository.add_or_update_icon_checksum(
            parent_id,
            checksums_data[parent_id],
        )
    t_end = timeit.default_timer()
    log.debug(f"Checksum saver {t_end - t}")
    log.info("New checksum saved 📦")
    log.info(f"Script complete. Checksum updated")
