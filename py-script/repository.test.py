from dotenv import load_dotenv

load_dotenv()

import utils
import repository

from constants import *
from qdrant_client import QdrantClient
from qdrant_client.http import models

arg = utils.parse_arg_update_checksum(
    DEFAULT_JSON_PATH,
)

qdrant_client = QdrantClient(
    url=arg.qdrant_endpoint,
    api_key=arg.qdrant_api_key,
)

collections = qdrant_client.get_collections().collections
print([collection.name for collection in collections])

# qdrant_client.upsert(
#     collection_name="test",
#     points=models.Batch(
#         ids=[
#             1,
#         ],
#         payloads=[
#             {"color": "red"},
#         ],
#         vectors=[
#             [0 for _ in range(300)],
#         ],
#     ),
# )

# res = qdrant_client.scroll(
#     collection_name="test",
# )


# print(res)
