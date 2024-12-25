FROM ubuntu:22.04

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Настройка для корректной работы protobuf:
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# Установка python
RUN apt update && apt install -y python3.10 python3-dev python3-pip

# Утилиты для Apache Tika
RUN apt install -y curl ssh gcc g++ && apt-get install -y libssl-dev libffi-dev libxml2-dev libxslt1-dev
RUN apt install -y openjdk-8-jdk ant ca-certificates-java && update-ca-certificates -f
RUN apt install -y libmagic1

# Утилиты для библиотеки patool (универсального разархиватора)
RUN apt install -y p7zip-full rar unrar-free unace unadf unalz arc arj bzip2 xdms lrzip lz4 lzip rzip zpaq zstd lhasa lzop sharutils flac file

# Утилита для библиотеки patool (bzip3 учтанавливается через brew)
RUN apt install -y git
RUN /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
ENV PATH="/home/linuxbrew/.linuxbrew/bin:${PATH}"
RUN brew install bzip3

WORKDIR /root

COPY ./build/requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .
COPY ./configs/gunicorn.conf.py .
COPY ./configs/ ./configs/
COPY ./internal/ ./internal/
COPY ./web/ ./web/
