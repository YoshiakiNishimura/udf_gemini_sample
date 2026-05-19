#!/bin/bash
# shfmt -w
#TSURUGI_PROTOは自分の環境に合わせて設定
PROTO_FILE="gemini.proto"
python3 -m grpc_tools.protoc \
	-Iproto -I ${TSURUGI_PROTO} \
	--python_out=proto \
	--grpc_python_out=proto \
	proto/${PROTO_FILE} 
udf-plugin-builder --proto proto/${PROTO_FILE}  \
	-I proto -I ${TSURUGI_PROTO} \
	--grpc-endpoint "dns:///localhost:40010" \
	--clean --debug --output-dir ${BASE_DIR}
