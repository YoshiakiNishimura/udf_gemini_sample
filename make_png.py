import argparse
import hashlib
import subprocess
from pathlib import Path


def escape_plantuml_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ensure_png_suffix(path: Path) -> Path:
    if path.suffix.lower() != ".png":
        return path.with_suffix(".png")
    return path


def make_plantuml_png_blob(text: str) -> bytes:
    safe_text = escape_plantuml_text(text)

    puml = f"""@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName SansSerif
skinparam defaultFontSize 24
title BLOB Test

rectangle "{safe_text}" as Target

@enduml
"""

    result = subprocess.run(
        ["plantuml", "-tpng", "-pipe"],
        input=puml.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    return result.stdout


def make_png_file(output_path: str) -> None:
    path = ensure_png_suffix(Path(output_path))

    base_text = path.stem
    ocr_text = f"hello {base_text}"

    png_bytes = make_plantuml_png_blob(ocr_text)

    path.write_bytes(png_bytes)

    print("png file =", path)
    print("ocr text =", ocr_text)
    print("size     =", len(png_bytes))
    print("sha256   =", sha256_hex(png_bytes))
    print("header   =", png_bytes[:16])
    print("is png   =", png_bytes.startswith(b"\x89PNG\r\n\x1a\n"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a PlantUML PNG file for OCR/BLOB testing."
    )
    parser.add_argument(
        "output_path",
        help="Output PNG filename. If .png is omitted, it is added automatically.",
    )

    args = parser.parse_args()
    make_png_file(args.output_path)


if __name__ == "__main__":
    main()
