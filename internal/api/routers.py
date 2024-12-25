import os.path

from fastapi import APIRouter, HTTPException
from configs.config import INPUT_DIR
from internal.api.schemas import TikaFileExtract, ListTikaFileExtractResult
from internal.extractors.tika_extractor import base_extract_with_schema

tika_router = APIRouter(
    prefix="/extract_from_file",
    tags=["Извлечение информации из файла"]
)
routes = [tika_router]


@tika_router.post("", response_model=ListTikaFileExtractResult,
                  summary="Извлечение плоского текста и метаданных из файла",
                  description="filename - название файла (файл должен находится в папке input_dir)")
async def extract_from_file(task: TikaFileExtract) -> ListTikaFileExtractResult:
    if not os.path.exists(os.path.join(INPUT_DIR, task.filename)):
        raise HTTPException(status_code=404, detail=f"File {task.filename} not found in input_dir")
    return base_extract_with_schema(task.filename)
