import datetime
import os
from email import policy
import patoolib
from hashlib import sha256
from typing import Dict
import extract_msg
import email

from configs.config import INPUT_DIR


def _save_file(filename: str, data: str) -> None:
    """
    Сохранение данных в файл.
    :param filename: Полный путь до нового файла.
    :param data: Текст.
    :return: None.
    """
    with open(filename, 'w', encoding='utf-8') as n_file:
        n_file.write(data)


def _create_unique_dir_name(path: str) -> str:
    """
    Создание уникального имени для папки содержащее название файла.
    :param path: Путь до файла.
    :return: Уникальное имя папки.
    """
    time = datetime.datetime.now()
    size = os.path.getsize(path)
    return f"{os.path.basename(path)}_{sha256(f'{path}_{size}_{time}'.encode('utf-8')).hexdigest()}"


def _unpack_email(email_file: str, source_dir: str) -> Dict[str, str]:
    """
    Распаковка писем форматов .msg, .eml и .emlx.
    :param email_file: Название файла.
    :param source_dir: Путь до папки с архивом.
    :return: Название новой папки temp_dir с разархивированными файлами или сообщение об ошибке.
    """
    file_ext = os.path.splitext(email_file)[1]
    email_with_source_dir = os.path.join(source_dir, email_file)
    unpack_dir_name = _create_unique_dir_name(email_with_source_dir)
    new_folder = os.path.join(source_dir, unpack_dir_name)
    os.mkdir(new_folder)

    if file_ext == 'msg':
        try:
            msg = extract_msg.Message(email_with_source_dir)
            msg.saveAttachments(customPath=new_folder)
            _save_file(os.path.join(new_folder, 'raw_message_text.txt'), f'{msg.header}\n{msg.body}')
            msg.close()
            # os.remove(email_with_source_dir)
            return {'success': unpack_dir_name}
        except:
            os.remove(new_folder)
            return {'error': f"File {email} can't extract"}
    else:
        try:
            with open(email_with_source_dir, 'r') as file:
                email_message = email.message_from_file(file, policy=policy.default)
                _save_file(os.path.join(new_folder, 'raw_message_text.txt'), email_message.as_string())
                attachments = [item for item in email_message.iter_attachments() if item.is_attachment()]
                if attachments:
                    for attachment in attachments:
                        filename = attachment.get_filename()
                        data = attachment.get_payload(decode=True)
                        with open(os.path.join(new_folder, filename), 'wb') as n_file:
                            n_file.write(data)
            # os.remove(email_with_source_dir)
            return {'success': unpack_dir_name}
        except:
            os.remove(new_folder)
            return {'error': f"File {email} can't extract"}


def unpack(archive: str, input_dir: str) -> Dict[str, str]:
    """
    Извлечение содержимого архива archive в temp_dir внутри input_dir с последующим удалением источника.
    Возвращение названия temp_dir.

    :param archive: Название архива.
    :param input_dir: Путь до папки с архивом.
    :return: Название новой папки temp_dir с разархивированными файлами или сообщение об ошибке.
    """
    archive_ext = os.path.splitext(archive)[1]

    # Неподдерживаемые типы архивов (не найдено рабочих утилит)
    unsupported_types = ['ape', 'shn', 'zoo']
    if archive_ext in unsupported_types:
        return {'error': f'File {archive} is not archive'}

    # Извлечение файлов из писем
    email_archives = ['msg', 'eml', 'emlx']
    if archive_ext in email_archives:
        return _unpack_email(archive, input_dir)

    # Извлечение из остальных архивов
    archive_with_source_dir = os.path.join(input_dir, archive)
    if patoolib.is_archive(archive_with_source_dir):
        # Проверка целостности и наличия пароля
        try:
            patoolib.test_archive(archive_with_source_dir, verbosity=-1)
        except patoolib.util.PatoolError:
            return {'error': f'File {archive} broken or encrypted'}

        # Попытка извлечения
        try:
            # Создание уникального имени временной папки
            unpack_dir_name = _create_unique_dir_name(archive_with_source_dir)
            out_dir = os.path.join(input_dir, unpack_dir_name)

            patoolib.extract_archive(archive_with_source_dir, outdir=out_dir, verbosity=-1)
            # os.remove(archive_with_source_dir)
            return {'success': out_dir}
        except patoolib.util.PatoolError:
            return {'error': f"File {archive} can't extract"}
    return {'error': f'File {archive} is not archive'}


def multi_unpack(archive: str, input_dir: str) -> Dict[str, str]:
    """
    Рекурсивная распаковка архива и содержащихся внутри архивов.
    """
    unpack_res = unpack(archive=archive, input_dir=input_dir)
    if list(unpack_res.keys())[0] == 'success':
        unpack_dir_name = os.path.join(INPUT_DIR, unpack_res['success'])

        unpacked_archives = []
        while True:
            files = [os.path.join(root, name) for root, _, files in os.walk(unpack_dir_name) for name in files]
            files = [file for file in files if file not in unpacked_archives]
            count = 0
            for file in files:
                if patoolib.is_archive(file):
                    unpack(archive=os.path.basename(file), input_dir=os.path.dirname(file))
                    unpacked_archives.append(file)
                    count += 1

            if count == 0:
                break
    return unpack_res
