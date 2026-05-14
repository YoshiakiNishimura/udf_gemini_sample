#!/bin/bash
# shfmt -w
PROTO_FILE="gemini.proto"
python3 -m grpc_tools.protoc \
	-Iproto  \
	--python_out=proto \
	--grpc_python_out=proto \
	proto/${PROTO_FILE} 
udf-plugin-builder --proto proto/${PROTO_FILE}  \
	-I proto \
	--grpc-endpoint "dns:///localhost:40010" \
	--clean --debug --output-dir ${BASE_DIR}
