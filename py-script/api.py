from dotenv import load_dotenv

load_dotenv()

import os
import re
import jwt
import core
import base64
import pymilvus
import typing
import constants
import requests
import datetime

import numpy as np

from PIL import Image
from io import BytesIO
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",
]


class CollectionInfo(BaseModel):
    embedder: str
    index: str
    collectionName: str


class Icon(BaseModel):
    iconID: str
    parentID: str
    iconName: str


class ImageEstimator:
    milvus_client_alias = "default"
    max_query_limit = 50

    def __init__(
        self,
        jwt_secret: str,
        hcaptcha_secret: str,
        milvus_uri: str,
        milvus_api_key: str,
        milvus_db: str,
    ) -> None:
        super().__init__()
        pymilvus.connections.connect(
            alias=self.milvus_client_alias,
            uri=milvus_uri,
            token=milvus_api_key,
            db_name=milvus_db,
        )
        self.hcaptcha_secret = hcaptcha_secret
        self.jwt_secret = jwt_secret

        # Prepare Collection
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

    def QueryImage(
        self,
        token: str,
        collectionName: str,
        base64Image: str,
        normalizeImage: bool,
        invertImage: bool,
        limit: int,
    ):
        # Todo Check Token
        if not self.CheckToken(token):
            raise HTTPException(401)

        # Check Request
        if limit > self.max_query_limit:
            limit = self.max_query_limit
        collection_name = collectionName
        collection_info = self.get_collection_info_by_name(collection_name)
        if collection_info is None:
            raise HTTPException(400)
        embedder_name = collection_info.embedder
        if embedder_name not in constants.EMBEDDER_DICT:
            raise HTTPException(500)

        # Prepare dependency
        embedder = constants.EMBEDDER_DICT[embedder_name]
        collection = pymilvus.Collection(
            name=collection_info.full_name, using=self.milvus_client_alias
        )

        # Get Image Embeddings
        image_data = re.sub("^data:image/.+;base64,", "", base64Image)
        img = Image.open(BytesIO(base64.b64decode(image_data)))
        img = img.convert("L")
        img_arr = np.array(img)
        if normalizeImage:
            img_arr = img_arr / 255
        if invertImage:
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
            limit=limit,
            consistency_level="Strong",
        )
        if not isinstance(results, pymilvus.SearchResult):
            raise HTTPException(500)

        # Re assign results
        results = results
        results_deep = results[0]
        if not isinstance(results_deep, pymilvus.Hits):
            raise HTTPException(500)

        icons = [
            Icon(
                iconID=res.entity.get("id"),
                parentID=res.entity.get("parent_name"),
                iconName=res.entity.get("icon_name"),
            )
            for res in results_deep
        ]
        return icons

    def GetCollectionInfo(self):
        return [
            CollectionInfo(
                embedder=collection.embedder,
                index=collection.index,
                collectionName=collection.full_name,
            )
            for collection in self.collections_info
        ]

    def CreateToken(self, responseToken: str) -> str:
        if not self._validateHcaptcha(responseToken):
            raise HTTPException(400)

        expired_at = datetime.datetime.now()
        expired_at += datetime.timedelta(days=1)
        jwt_str = jwt.encode(
            {"exp": expired_at.timestamp()}, self.jwt_secret, algorithm="HS256"
        )

        return jwt_str

    def CheckToken(self, token: str) -> bool:
        try:
            jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return True
        except:
            return False

    def _validateHcaptcha(self, responseToken: str) -> bool:
        # Build payload with secret key and token.
        data = {
            "secret": self.hcaptcha_secret,
            "response": responseToken,
        }

        # Make POST request with data payload to hCaptcha API endpoint.
        response = requests.post(
            url="https://hcaptcha.com/siteverify",
            data=data,
        )

        # Parse JSON from response. Check for success or error codes.
        response_json = response.json()
        success = response_json["success"]

        return success


app = FastAPI(
    title="Draw React Icons Queries API",
)

if os.environ["HCAPTCHA_SECRET"].strip() == "":
    raise ValueError("AUTH_SECRET Environment variable need to be set")

exec = ImageEstimator(
    os.environ["JWT_SECRET"] or "",
    os.environ["HCAPTCHA_SECRET"] or "",
    os.environ["MILVUS_ENDPOINT"] or "",
    os.environ["MILVUS_API_KEY"] or "",
    os.environ["MILVUS_DB"] or "",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["health"])
def read_root():
    return "Hello World"


@app.get("/auth", tags=["authentication"])
def check_token(token: str) -> bool:
    return exec.CheckToken(token)


@app.post("/auth/tokens", tags=["authentication"])
def create_token(hCaptchaToken: str) -> str:
    return exec.CreateToken(hCaptchaToken)


@app.get("/collections", tags=["collections"])
def get_collections() -> list[CollectionInfo]:
    return exec.GetCollectionInfo()


@app.post("/collections/query", tags=["collections"])
def query_collections(
    token: str,
    collectionName: str,
    base64Image: str,
    normalizeImage: bool = True,
    invertImage: bool = False,
    limit: int = 20,
) -> list[Icon]:
    return exec.QueryImage(
        token, collectionName, base64Image, normalizeImage, invertImage, limit
    )
