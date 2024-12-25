import asyncio
from typing import Iterator

import grpc.aio

from configs.config import TIKA_EXTRACTOR_SERVICE_GRPC_PORT
from internal.api.grpc.proto.compiled.tika_file_extract_pb2 import TikaFileExtractResult, ListTikaFileExtractResult, \
    TikaFileExtract
from internal.api.grpc.proto.compiled.tika_file_extract_service_pb2_grpc import TikaFileExtractorServicer, \
    add_TikaFileExtractorServicer_to_server
from internal.extractors.tika_extractor import base_extractor


def base_extract_with_proto(filename: str):
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
    return results


class TikaFileExtractor(TikaFileExtractorServicer):
    def ExtractFromFile(
            self,
            request: TikaFileExtract,
            context: grpc.aio.ServicerContext) -> ListTikaFileExtractResult:
        results = base_extract_with_proto(filename=request.filename)
        return ListTikaFileExtractResult(results=results)

    def ExtractFromFileClientStream(
            self,
            request_iterator: Iterator[TikaFileExtract],
            context: grpc.aio.ServicerContext) -> ListTikaFileExtractResult:
        for r in request_iterator:
            results = base_extract_with_proto(filename=r.filename)
            yield ListTikaFileExtractResult(results=results)


async def grpc_start() -> None:
    server = grpc.aio.server()
    add_TikaFileExtractorServicer_to_server(TikaFileExtractor(), server)
    server.add_insecure_port(f"0.0.0.0:{TIKA_EXTRACTOR_SERVICE_GRPC_PORT}")
    await server.start()
    await server.wait_for_termination()


def run_grpc_server() -> None:
    asyncio.run(grpc_start())
