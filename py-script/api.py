from dotenv import load_dotenv

load_dotenv()

import re
import os
import core
import grpc
import base64
import logging
import pymilvus
import typing
import constants
import numpy as np

from PIL import Image
from io import BytesIO

# gRPC related
from rpc import (
    draw_react_icons_pb2,
    draw_react_icons_pb2_grpc,
)

from concurrent import futures
from grpc_reflection.v1alpha import reflection


class ImageEstimator(draw_react_icons_pb2_grpc.IconEstimatorServicer):
    milvus_client_alias = "default"

    def __init__(self, milvus_uri: str, milvus_api_key: str, milvus_db: str) -> None:
        super().__init__()
        pymilvus.connections.connect(
            alias=self.milvus_client_alias,
            uri=milvus_uri,
            token=milvus_api_key,
            db_name=milvus_db,
        )
        collections = pymilvus.utility.list_collections(using=self.milvus_client_alias)
        self.collections_info: typing.List[core.CollectionInformation] = []
        for collection in collections:
            collection_data = pymilvus.Collection(
                name=collection, using=self.milvus_client_alias
            )
            try:
                self.collections_info.append(
                    core.CollectionInformation.from_json(
                        collection_data.description,
                    )
                )
            except:
                continue

    def get_collection_info_by_name(
        self, name: str
    ) -> core.CollectionInformation | None:
        for collection in self.collections_info:
            if collection.full_name == name:
                return collection
        return None

    def QueryImage(self, request, context):
        # TODO: Do Auth
        
        # Check Request
        collection_name = request.collectionName
        collection_info = self.get_collection_info_by_name(collection_name)
        if collection_info is None:
            return context.abort(
                code=grpc.StatusCode.INVALID_ARGUMENT, details="Invalid collection name"
            )
        embedder_name = collection_info.embedder
        if embedder_name not in constants.EMBEDDER_DICT:
            return context.abort(
                code=grpc.StatusCode.INTERNAL, details="Embedder not initialized"
            )

        # Prepare dependency
        embedder = constants.EMBEDDER_DICT[embedder_name]
        collection = pymilvus.Collection(
            name=collection_info.full_name, using=self.milvus_client_alias
        )

        # Get Image Embeddings
        image_data = re.sub("^data:image/.+;base64,", "", request.base64image)
        img = Image.open(BytesIO(base64.b64decode(image_data)))
        img = img.convert("L")
        img_arr = np.array(img)
        if request.normalizeImage:
            img_arr = img_arr / 255
        if request.invertImage:
            img_arr = (img_arr - 1) * -1
        embeddings = embedder.embeds(img_arr)

        # Query to Database
        search_params = {
            "metric_type": collection_info.index,
            "offset": 0,
            "ignore_growing": False,
            "params": {},
        }
        results = collection.search(
            data=[embeddings],
            anns_field="embedding",
            param=search_params,
            output_fields=["id", "parent_name", "icon_name"],
            limit=10,
            consistency_level="Strong",
        )
        if not isinstance(results, pymilvus.SearchResult):
            return context.abort(
                code=grpc.StatusCode.INTERNAL, details="Internal (res)"
            )

        # Re assign results
        results = results
        results_deep = results[0]
        if not isinstance(results_deep, pymilvus.Hits):
            return context.abort(
                code=grpc.StatusCode.INTERNAL, details="Internal (list)"
            )
        icons = [
            draw_react_icons_pb2.Icon(
                iconID=res.entity.get("id"),
                parentID=res.entity.get("parent_name"),
                iconName=res.entity.get("icon_name"),
            )
            for res in results_deep
        ]
        return draw_react_icons_pb2.Icons(icons=icons)

    def GetCollectionInfo(self, request, context):
        return draw_react_icons_pb2.Collections(
            collections=[
                draw_react_icons_pb2.Collection(
                    embedder=collection.embedder,
                    index=collection.index,
                    collectionName=collection.full_name,
                )
                for collection in self.collections_info
            ]
        )


if __name__ == "__main__":
    logging.basicConfig()
    port = "1323"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    draw_react_icons_pb2_grpc.add_IconEstimatorServicer_to_server(
        ImageEstimator(
            os.environ.get("MILVUS_ENDPOINT") or "",
            os.environ.get("MILVUS_API_KEY") or "",
            os.environ.get("MILVUS_DB") or "",
        ),
        server,
    )
    SERVICE_NAMES = (
        draw_react_icons_pb2.DESCRIPTOR.services_by_name["IconEstimator"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()
