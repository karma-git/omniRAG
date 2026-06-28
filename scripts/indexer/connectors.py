from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from loguru import logger


def extract_text_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def extract_text_pdf(path: Path) -> str:
    try:
        import pypdf  # noqa: PLC0415
    except ImportError:
        logger.warning("pypdf not installed — skipping {}", path)
        return ""
    reader = pypdf.PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


_EXTRACTORS = {
    ".txt": extract_text_txt,
    ".md": extract_text_txt,
    ".markdown": extract_text_txt,
    ".pdf": extract_text_pdf,
}


def iter_documents(docs_dir: Path, recursive: bool) -> Iterator[tuple[Path, str]]:
    glob = "**/*" if recursive else "*"
    for path in sorted(docs_dir.glob(glob)):
        if not path.is_file():
            continue
        extractor = _EXTRACTORS.get(path.suffix.lower())
        if extractor is None:
            logger.debug("Skipping unsupported file: {}", path)
            continue
        logger.info("Reading: {}", path.relative_to(docs_dir))
        text = extractor(path)
        if text.strip():
            yield path, text
        else:
            logger.warning("Empty content: {}", path)
