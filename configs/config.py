import os

from dotenv import load_dotenv

load_dotenv()
PUBLISH_QUEUE = os.environ.get("PUBLISH_QUEUE")
SUBSCRIBE_QUEUE = os.environ.get("SUBSCRIBE_QUEUE")
RABBITMQ_URL = os.environ.get("RABBITMQ_URL")

INPUT_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'input_dir')
OUTPUT_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output_dir')

TIKA_EXTRACTOR_SERVICE_GRPC_PORT = os.environ.get("TIKA_EXTRACTOR_SERVICE_GRPC_PORT")
