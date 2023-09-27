from dotenv import load_dotenv

load_dotenv()

import os
import re
import jwt
import core
import base64
import typing
import constants
import requests
import datetime

import numpy as np

from PIL import Image
from io import BytesIO
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http import models
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",
]

if os.environ.get("ENV") is not None and os.environ.get("ENV") == "production":
    origins = [
        "https://draw-react-icons.kaenova.my.id",
    ]


class CollectionInfo(BaseModel):
    embedder: str
    index: str
    collectionName: str


class Icon(BaseModel):
    iconName: str
    parentID: str


class ImageEstimator:
    max_query_limit = 50

    def __init__(
        self,
        jwt_secret: str,
        hcaptcha_secret: str,
        qdrant_uri: str,
        qdrant_api_key: str,
    ) -> None:
        super().__init__()
        self.qdrant_client = QdrantClient(
            url=qdrant_uri, api_key=qdrant_api_key, prefer_grpc=True
        )
        self.embedders = {}
        for embedder_name in constants.EMBEDDER_DICT:
            self.embedders[embedder_name] = constants.EMBEDDER_DICT[embedder_name]()
        self.hcaptcha_secret = hcaptcha_secret
        self.jwt_secret = jwt_secret

    @staticmethod
    def _checkValidCollectionName(name: str) -> typing.Tuple[str, str] | None:
        pattern = r"^([^\_]+)_([^\_]+)$"
        match = re.match(pattern, name)
        if match:
            embedder_name = match.group(1)
            indexing_name = match.group(2)
            return embedder_name, indexing_name
        else:
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
        collection_info = self._checkValidCollectionName(collection_name)
        if collection_info is None:
            raise HTTPException(400)
        embedder_name = collection_info[0]
        if embedder_name not in constants.EMBEDDER_DICT:
            raise HTTPException(500)
        collections = self.GetCollectionInfo()
        collections_name = [x.collectionName for x in collections]
        if collection_name not in collections_name:
            raise HTTPException(400)

        # Get Image Embeddings
        embedder = self.embedders[embedder_name]
        image_data = re.sub("^data:image/.+;base64,", "", base64Image)
        img = Image.open(BytesIO(base64.b64decode(image_data)))
        img = img.convert("L")
        img_arr = np.array(img)
        if normalizeImage:
            img_arr = img_arr / 255
        if invertImage:
            img_arr = (img_arr - 1) * -1
        img_arr = np.expand_dims(img_arr, -1).astype(np.float32)
        embeddings = embedder.embeds(img_arr)

        # Query to Database
        res = self.qdrant_client.search(
            collection_name=collection_name,
            search_params=models.SearchParams(exact=False),
            query_vector=embeddings,
            limit=limit,
        )

        queried_icons: typing.List[Icon] = []
        for point in res:
            if point.payload is None:
                continue
            icon_name = point.payload.get("icon_name")
            parent_id = point.payload.get("parent_id")
            if icon_name is None or parent_id is None:
                continue
            queried_icons.append(
                Icon(
                    iconName=icon_name,
                    parentID=parent_id,
                )
            )
        return queried_icons

    def GetCollectionInfo(self):
        collections = self.qdrant_client.get_collections().collections
        valid_collection: typing.List[CollectionInfo] = []
        for collection in collections:
            collection_info = ImageEstimator._checkValidCollectionName(collection.name)
            if collection_info is not None:
                valid_collection.append(
                    CollectionInfo(
                        embedder=collection_info[0],
                        index=collection_info[1],
                        collectionName=collection.name,
                    )
                )
        return valid_collection

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
    os.environ["QDRANT_ENDPOINT"] or "",
    os.environ["QDRANT_API_KEY"] or "",
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


class CollectionQuery(BaseModel):
    collectionName: str
    base64Image: str
    normalizeImage: bool = True
    invertImage: bool = False
    limit: int = 20


@app.post("/collections/query", tags=["collections"])
def query_collections(token: str, collectionQuery: CollectionQuery) -> list[Icon]:
    return exec.QueryImage(
        token,
        collectionQuery.collectionName,
        collectionQuery.base64Image,
        collectionQuery.normalizeImage,
        collectionQuery.invertImage,
        collectionQuery.limit,
    )
