from concurrent import futures
import logging
import os
import sys
from pathlib import Path

import grpc
from google import genai

PROTO_DIR = Path(__file__).resolve().parent / "proto"
sys.path.insert(0, str(PROTO_DIR))

import gemini_pb2
import gemini_pb2_grpc


client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def ask_gemini(prompt: str) -> str:
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"),
        contents=prompt,
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
