from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ImageQuery(_message.Message):
    __slots__ = ["base64image", "collectionName", "invertImage", "normalizeImage"]
    BASE64IMAGE_FIELD_NUMBER: _ClassVar[int]
    COLLECTIONNAME_FIELD_NUMBER: _ClassVar[int]
    INVERTIMAGE_FIELD_NUMBER: _ClassVar[int]
    NORMALIZEIMAGE_FIELD_NUMBER: _ClassVar[int]
    base64image: str
    collectionName: str
    invertImage: bool
    normalizeImage: bool
    def __init__(self, base64image: _Optional[str] = ..., collectionName: _Optional[str] = ..., invertImage: bool = ..., normalizeImage: bool = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class Icon(_message.Message):
    __slots__ = ["iconID", "parentID", "iconName"]
    ICONID_FIELD_NUMBER: _ClassVar[int]
    PARENTID_FIELD_NUMBER: _ClassVar[int]
    ICONNAME_FIELD_NUMBER: _ClassVar[int]
    iconID: str
    parentID: str
    iconName: str
    def __init__(self, iconID: _Optional[str] = ..., parentID: _Optional[str] = ..., iconName: _Optional[str] = ...) -> None: ...

class Icons(_message.Message):
    __slots__ = ["icons"]
    ICONS_FIELD_NUMBER: _ClassVar[int]
    icons: _containers.RepeatedCompositeFieldContainer[Icon]
    def __init__(self, icons: _Optional[_Iterable[_Union[Icon, _Mapping]]] = ...) -> None: ...

class Collections(_message.Message):
    __slots__ = ["collections"]
    COLLECTIONS_FIELD_NUMBER: _ClassVar[int]
    collections: _containers.RepeatedCompositeFieldContainer[Collection]
    def __init__(self, collections: _Optional[_Iterable[_Union[Collection, _Mapping]]] = ...) -> None: ...

class Collection(_message.Message):
    __slots__ = ["embedder", "index", "collectionName"]
    EMBEDDER_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    COLLECTIONNAME_FIELD_NUMBER: _ClassVar[int]
    embedder: str
    index: str
    collectionName: str
    def __init__(self, embedder: _Optional[str] = ..., index: _Optional[str] = ..., collectionName: _Optional[str] = ...) -> None: ...
