#!/usr/bin/env bash
# 最新のplantumlを使用すること
#curl -L \
#  https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar \
#  -o /opt/plantuml/plantuml.jar
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PUML_DIR="${ROOT_DIR}/plantuml"
IMG_DIR="${ROOT_DIR}/images"
TMP_DIR="${ROOT_DIR}/.diagram_tmp"

mkdir -p "${IMG_DIR}" "${TMP_DIR}"
rm -rf "${TMP_DIR:?}/"*

if command -v magick >/dev/null 2>&1; then
  IM="magick"
elif command -v convert >/dev/null 2>&1; then
  IM="convert"
else
  echo "ERROR: ImageMagick is required. Install imagemagick." >&2
  exit 1
fi

if ! command -v plantuml >/dev/null 2>&1; then
  echo "ERROR: plantuml is required. Install plantuml." >&2
  exit 1
fi

build_one() {
  local src="$1"
  local width="$2"
  local height="$3"

  local base
  base="$(basename "${src}" .puml)"

  local raw="${TMP_DIR}/${base}.png"
  local out="${IMG_DIR}/${base}.png"

  plantuml -tpng -o "${TMP_DIR}" "${src}"

  local generated=""
  generated="$(find "${TMP_DIR}" "${PUML_DIR}/.diagram_tmp" -name "${base}.png" 2>/dev/null | head -n 1 || true)"

  if [[ -z "${generated}" && -f "${PUML_DIR}/${base}.png" ]]; then
    generated="${PUML_DIR}/${base}.png"
  fi

  if [[ -z "${generated}" || ! -f "${generated}" ]]; then
    echo "ERROR: generated PNG not found for ${src}" >&2
    exit 1
  fi

  "${IM}" "${generated}" \
    -background "#F8FAFC" \
    -gravity center \
    -extent "${width}x${height}" \
    "${out}"

  echo "generated: ${out}"
}

build_one "${PUML_DIR}/01_eyecatch_note_1280x670.puml" 1280 670
build_one "${PUML_DIR}/02_architecture_body_1280x720.puml" 1280 720
build_one "${PUML_DIR}/03_execution_flow_body_1280x720.puml" 1280 720
build_one "${PUML_DIR}/04_blob_processing_body_1280x720.puml" 1280 720

echo
echo "Done."
echo "Check sizes:"
file "${IMG_DIR}"/*.png
