import threading

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html

from configs.config import RABBITMQ_URL, TIKA_EXTRACTOR_SERVICE_GRPC_PORT
from internal.api.grpc.grpc import run_grpc_server
from internal.api.routers import routes
from internal.api.rabbit import get_from_rabbit

app = FastAPI(title="Tika extractor service", docs_url=None, redoc_url=None)
app.mount("/web", StaticFiles(directory="web"), name="web")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in routes:
    app.include_router(r)


@app.get("/", include_in_schema=False)
def get_root() -> RedirectResponse:
    return RedirectResponse("/docs")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title,
        swagger_js_url="/web/swagger/swagger.js",
        swagger_css_url="/web/swagger/swagger.css",
    )


@app.on_event("startup")
async def startup_event():
    # Rabbit start
    if RABBITMQ_URL:
        threading.Thread(target=get_from_rabbit, daemon=True).start()

    # gRPC start
    if TIKA_EXTRACTOR_SERVICE_GRPC_PORT:
        threading.Thread(target=run_grpc_server, daemon=True).start()
