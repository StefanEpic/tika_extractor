import json
from time import sleep

from pika.adapters.blocking_connection import BlockingConnection
from pika.connection import URLParameters
from pika.exceptions import AMQPConnectionError

from configs.config import SUBSCRIBE_QUEUE, PUBLISH_QUEUE, RABBITMQ_URL
from internal.extractors.tika_extractor import base_extractor


def send_to_rabbit(data: str) -> None:
    """
    Отправить data в очередь PUBLISH_QUEUE rabbitmq RABBITMQ_URL.
    """
    with BlockingConnection(URLParameters(RABBITMQ_URL)) as conn:
        with conn.channel() as ch:
            ch.basic_publish(
                exchange="",
                routing_key=PUBLISH_QUEUE,
                body=data
            )


def extract_text_from_rabbit(*args) -> None:
    """
    Обработка результатов из очереди и направление результатов в rabbitmq.
    """
    result = {"status_code": 422, "detail": 'Incorrect input format'}
    try:
        request = json.loads(args[-1].decode('utf-8'))
        filename = request.get("filename", None)
        if filename is None:
            send_to_rabbit(data=json.dumps(result))
            return

        if filename:
            result = base_extractor(filename=filename)

    except json.decoder.JSONDecodeError:
        pass
    send_to_rabbit(data=json.dumps(result))


def create_rabbit_queue() -> None:
    """
    Создать очереди SUBSCRIBE_QUEUE и PUBLISH_QUEUE в rabbitmq RABBITMQ_URL.
    """
    try:
        sleep(10)
        with BlockingConnection(URLParameters(RABBITMQ_URL)) as conn:
            with conn.channel() as ch:
                ch.queue_declare(queue=SUBSCRIBE_QUEUE)
                ch.queue_declare(queue=PUBLISH_QUEUE)
    except AMQPConnectionError:
        sleep(20)
        with BlockingConnection(URLParameters(RABBITMQ_URL)) as conn:
            with conn.channel() as ch:
                ch.queue_declare(queue=SUBSCRIBE_QUEUE)
                ch.queue_declare(queue=PUBLISH_QUEUE)


def get_from_rabbit() -> None:
    """
    Начать прослушивание очереди SUBSCRIBE_QUEUE в rabbitmq RABBITMQ_URL.
    """
    create_rabbit_queue()
    with BlockingConnection(URLParameters(RABBITMQ_URL)) as conn:
        with conn.channel() as ch:
            ch.basic_consume(
                queue=SUBSCRIBE_QUEUE,
                on_message_callback=extract_text_from_rabbit,
                auto_ack=True,
                consumer_tag="tika_extractor_service"
            )
            ch.start_consuming()
