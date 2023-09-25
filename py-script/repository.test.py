from dotenv import load_dotenv

load_dotenv()

import utils
import repository

from constants import *
from qdrant_client import QdrantClient
from qdrant_client.http import models

arg = utils.parse_arg_api(
    EMBEDDER_DICT,
)

qdrant_client = QdrantClient(
    url=arg.qdrant_endpoint,
    api_key=arg.qdrant_api_key,
    prefer_grpc=True,
)

collections = qdrant_client.get_collections().collections

qdrant_client.upsert(
    collection_name="test",
    points=models.Batch(
        ids=[2],
        payloads=[
            {"color": "red", "mantap": {"jasdasd": "asdlasdkl"}},
        ],
        vectors=[
            [0 for _ in range(300)],
        ],
    ),
)

res = qdrant_client.scroll(
    collection_name="test",
)
