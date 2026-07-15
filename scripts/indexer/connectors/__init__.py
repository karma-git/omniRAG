"""Document-source adapters used by the indexer."""

from scripts.indexer.connectors.base import DocumentSource, SourceDocument
from scripts.indexer.connectors.filesystem import FilesystemSource, iter_documents

__all__ = ["DocumentSource", "FilesystemSource", "SourceDocument", "iter_documents"]
