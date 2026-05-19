from concurrent import futures
import logging
import os
import sys
from pathlib import Path
import tempfile
from datetime import timedelta
import hashlib
from tsurugidb.udf import create_blob_client

import grpc
from google import genai
from google.genai import types

PROTO_DIR = Path(__file__).resolve().parent / "proto"
sys.path.insert(0, str(PROTO_DIR))

import gemini_pb2
import gemini_pb2_grpc

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blob_ref_to_bytes(blob_ref, context) -> bytes:
    with create_blob_client(context) as blob_client:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "input.png"

            blob_client.download_blob(
                blob_ref,
                path,
                timeout=timedelta(seconds=60),
            )

            return path.read_bytes()


def assert_png(data: bytes) -> None:
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("BLOB data is not PNG")


def ask_gemini(prompt: str) -> str:
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"),
        contents=prompt,
    )
    return response.text or ""


def read_text_from_image_blob(image_bytes: bytes, mime_type: str = "image/png") -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=[
            "この画像に書かれている文字を、できるだけ正確に読み取ってください。",
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type,
            ),
        ],
    )
    return response.text or ""


class GeminiService(gemini_pb2_grpc.gemini_serviceServicer):
    def ask_gemini(self, request, context):
        try:
            answer = ask_gemini(request.str_value)
            return gemini_pb2.gemini_string(str_value=answer)

        except Exception as e:
            logging.exception("ask_gemini failed")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return gemini_pb2.gemini_string(str_value="")

    def ask_gemini_with_blob(self, request, context):
        try:
            logging.info("ask_gemini_with_blob called")

            if not request.HasField("blob_value"):
                raise ValueError("blob_value is NULL")

            blob = request.blob_value
            logging.info(
                "blob_value: storage_id=%s object_id=%s tag=%s provisioned=%s",
                blob.storage_id,
                blob.object_id,
                blob.tag,
                blob.provisioned,
            )

            image_bytes = blob_ref_to_bytes(request.blob_value, context)
            assert_png(image_bytes)

            logging.info("png size=%d", len(image_bytes))
            logging.info("png sha256=%s", sha256_hex(image_bytes))
            logging.info("png header=%r", image_bytes[:16])

            answer = read_text_from_image_blob(
                image_bytes,
                mime_type="image/png",
            )

            return gemini_pb2.gemini_string(str_value=answer)

        except Exception as e:
            logging.exception("ask_gemini_with_blob failed")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return gemini_pb2.gemini_string(str_value="")


def serve():
    port = os.getenv("PORT", "40010")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    gemini_pb2_grpc.add_gemini_serviceServicer_to_server(
        GeminiService(),
        server,
    )

    server.add_insecure_port("[::]:" + port)
    server.start()

    print(f"Gemini gRPC server started, listening on {port}")
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    serve()
