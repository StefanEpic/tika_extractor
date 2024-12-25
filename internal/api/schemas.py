from typing import List

from pydantic import BaseModel


class TikaFileExtract(BaseModel):
    filename: str


class TikaFileExtractResult(BaseModel):
    filename: str
    path: str
    mime_type: str
    content: str


class ListTikaFileExtractResult(BaseModel):
    results: List[TikaFileExtractResult]
