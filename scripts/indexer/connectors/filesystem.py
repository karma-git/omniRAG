from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from loguru import logger

from scripts.indexer.connectors.base import SourceDocument
from scripts.indexer.embed_cache import EmbedCache


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
    """Backward-compatible filesystem iterator."""
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


class FilesystemSource:
    def __init__(self, docs_dir: Path, recursive: bool = True) -> None:
        self._docs_dir = docs_dir
        self._recursive = recursive

    def iter_documents(self, cache: EmbedCache | None = None) -> list[SourceDocument]:
        del cache
        return [
            SourceDocument(text=text, source=str(path.relative_to(self._docs_dir)))
            for path, text in iter_documents(self._docs_dir, self._recursive)
        ]
