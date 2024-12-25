import io
import os
import shutil
from typing import List, Dict

from PIL import Image, UnidentifiedImageError
from tika import parser, unpack

from configs.config import OUTPUT_DIR, INPUT_DIR
from internal.api.schemas import ListTikaFileExtractResult, TikaFileExtractResult
from internal.extractors.universal_arch_extracter import _create_unique_dir_name, multi_unpack


def move_to_output_dir(file: str) -> str:
    """
    Перенос файла или каталога в OUTPUT_DIR.
    """
    unique_dir_name = _create_unique_dir_name(file)
    output_unique_dir_name = os.path.join(OUTPUT_DIR, unique_dir_name)
    os.mkdir(output_unique_dir_name)
    shutil.move(file, output_unique_dir_name)
    return os.path.basename(output_unique_dir_name)


def tika_extract(file: str) -> List[str]:
    """
    Извлечение content_type и content с помощью Apache Tika.
    """
    try:
        content_type = parser.from_file(file, serverEndpoint="http://localhost:9998/tika")["metadata"]["Content-Type"]
        content = parser.from_file(file, serverEndpoint="http://localhost:9998/tika")["content"]
        if isinstance(content_type, list):
            content_type = content_type[0]
        if content is None:
            content = "Can't extract from this file"
        return [content_type, content]
    except:
        return ["Content type not defined", "Can't extract from this file"]


def tika_extract_attachments(file: str) -> None:
    """
    Извлечение изображений из файла с помощью Apache Tika.
    """
    try:
        images = unpack.from_file(file, "http://localhost:9998/tika")["attachments"]
        img_list = []
        if images:
            for k, v in images.items():
                io_bytes = io.BytesIO(v)
                try:
                    img = Image.open(io_bytes)
                    try:
                        img.save(f'{file}_attachment_{k}')
                        img_list.append(f'{file}_attachment_{k}')
                    except (FileNotFoundError, OSError):
                        pass
                except UnidentifiedImageError:
                    pass
            if img_list:
                unique_dir_name = _create_unique_dir_name(file)
                dir_for_attachments = os.path.join(os.path.dirname(file), unique_dir_name)
                os.mkdir(dir_for_attachments)
                for i in img_list:
                    shutil.move(os.path.join(os.path.dirname(file), i), dir_for_attachments)
    except KeyError:
        pass


def extract_text_from_file(filename: str) -> List[str]:
    """
    Извлечение content_type, content и изображений из файла.
    """
    file = os.path.join(INPUT_DIR, filename)
    output_unique_dir_name = move_to_output_dir(file=file)
    file = os.path.join(OUTPUT_DIR, output_unique_dir_name, filename)
    content_type, content = tika_extract(file=file)
    tika_extract_attachments(file=file)
    return [output_unique_dir_name, content_type, content]


def base_extractor(filename: str) -> List[Dict[str, str]]:
    """
    Основная функция для извлечения информации из файла.
    Рекурсивно распаковывает архивы и извлекает данные.
    """
    result = []
    unpack_res = multi_unpack(archive=filename, input_dir=INPUT_DIR)
    # Если файл архив
    if list(unpack_res.keys())[0] == 'success':
        unpack_dir_name = os.path.join(INPUT_DIR, unpack_res['success'])
        files = [(root, name) for root, _, files in os.walk(unpack_dir_name) for name in files]
        for file in files:
            filename_with_path = os.path.join(file[0], file[1])
            content_type, content = tika_extract(file=filename_with_path)
            tika_extract_attachments(file=filename_with_path)
            result.append({
                "filename": file[1],
                "path": file[0].replace(INPUT_DIR, ''),
                "content_type": content_type,
                "content": content
            })
        shutil.move(unpack_dir_name, OUTPUT_DIR)
        os.remove(os.path.join(INPUT_DIR, filename))
    # Если файл не архив
    elif list(unpack_res.keys())[0] == 'error' and 'is not archive' in list(unpack_res.values())[0]:
        output_unique_dir_name, content_type, content = extract_text_from_file(filename)
        result.append({
            "filename": os.path.basename(filename),
            "path": output_unique_dir_name,
            "content_type": content_type,
            "content": content
        })
    # Неподдерживаемый файл
    else:
        output_unique_dir_name = move_to_output_dir(file=os.path.join(INPUT_DIR, filename))
        result.append({
            "filename": os.path.basename(filename),
            "path": output_unique_dir_name,
            "content_type": "",
            "content": f"Archive {filename} can't extract"
        })

    return result


def base_extract_with_schema(filename: str) -> ListTikaFileExtractResult:
    """
    Оформление результатов работы base_extractor в виде Pydantic schemas.
    """
    results = []
    for item in base_extractor(filename=filename):
        results.append(
            TikaFileExtractResult(
                filename=item['filename'],
                path=item['path'],
                mime_type=item['content_type'],
                content=item['content']
            )
        )
    return ListTikaFileExtractResult(results=results)
