## TikaExtractorService

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=flat&logo=gunicorn&logoColor=white)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-FF6600?style=flat&logo=rabbitmq&logoColor=white)
![gRPC](https://img.shields.io/badge/gRPC-19C4BE?style=flat&logo=gRPC&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)

АPI для извлечения плоского текста

## Назначение
Распаковка архивов и файлов-контейнеров ('msg', 'eml', 'emlx') с поледующим рекурсивным извлечением плоского текста из всех файлов контейнера и определение их MIME типа.

1. Файлы для извлечения необходимо перенести в input_dir.
2. Результаты обработки перемещаются в output_dir.
3. Помимо отправки задания методом POST на /extract_from_file также возможна отправка через RabbitMQ или gRPC.
