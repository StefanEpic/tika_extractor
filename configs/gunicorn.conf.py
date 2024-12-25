"""gunicorn WSGI server configuration."""

import os

from dotenv import load_dotenv

load_dotenv()
TIKA_EXTRACTOR_SERVICE_PORT = os.environ.get("TIKA_EXTRACTOR_SERVICE_PORT")

bind = f"0.0.0.0:{TIKA_EXTRACTOR_SERVICE_PORT}"
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 0
workers = 2 * os.cpu_count() + 1
default_proc_name = "tika_extractor_service"
accesslog = "-"
errorlog = "-"
