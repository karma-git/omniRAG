"""Confluence Cloud and Server/Data Center document source.

Required ENV:
  CONFLUENCE_BASE_URL
  Cloud: CONFLUENCE_EMAIL + CONFLUENCE_API_TOKEN
  Server/DC: CONFLUENCE_PAT
  CONFLUENCE_SPACE_KEYS and/or CONFLUENCE_CQL
Optional:
  CONFLUENCE_DEPLOYMENT=cloud|server (default: cloud)
  CONFLUENCE_WORKERS=6
"""

from __future__ import annotations

import hashlib
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Protocol
from urllib.parse import urljoin

import httpx
from loguru import logger

from app.core.normalizer import normalize
from scripts.indexer.connectors.base import SourceDocument
from scripts.indexer.embed_cache import EmbedCache

_RETRY_STATUSES = {429, 502, 503, 504}


class ConfluenceAuthProvider(Protocol):
    def apply(self, client_kwargs: dict) -> None: ...


@dataclass(frozen=True)
class CloudBasicAuth:
    email: str
    api_token: str

    def apply(self, client_kwargs: dict) -> None:
        client_kwargs["auth"] = httpx.BasicAuth(self.email, self.api_token)


@dataclass(frozen=True)
class BearerAuth:
    token: str

    def apply(self, client_kwargs: dict) -> None:
        client_kwargs.setdefault("headers", {})["Authorization"] = f"Bearer {self.token}"


@dataclass(frozen=True)
class ConfluenceConfig:
    base_url: str
    deployment: str
    space_keys: tuple[str, ...]
    cql: str | None
    workers: int
    auth: ConfluenceAuthProvider

    @classmethod
    def from_env(cls) -> ConfluenceConfig:
        base_url = os.getenv("CONFLUENCE_BASE_URL", "").strip()
        deployment = os.getenv("CONFLUENCE_DEPLOYMENT", "cloud").strip().lower()
        spaces = tuple(
            item.strip()
            for item in os.getenv("CONFLUENCE_SPACE_KEYS", "").split(",")
            if item.strip()
        )
        cql = os.getenv("CONFLUENCE_CQL", "").strip() or None
        workers = int(os.getenv("CONFLUENCE_WORKERS", "6"))

        if not base_url:
            raise ValueError("CONFLUENCE_BASE_URL is required")
        if deployment not in {"cloud", "server"}:
            raise ValueError("CONFLUENCE_DEPLOYMENT must be cloud or server")
        if not spaces and not cql:
            raise ValueError("CONFLUENCE_SPACE_KEYS or CONFLUENCE_CQL is required")
        if workers < 1:
            raise ValueError("CONFLUENCE_WORKERS must be at least 1")

        if deployment == "cloud":
            email = os.getenv("CONFLUENCE_EMAIL", "")
            token = os.getenv("CONFLUENCE_API_TOKEN", "")
            if not email or not token:
                raise ValueError(
                    "Confluence Cloud requires CONFLUENCE_EMAIL and CONFLUENCE_API_TOKEN"
                )
            auth: ConfluenceAuthProvider = CloudBasicAuth(email, token)
        else:
            token = os.getenv("CONFLUENCE_PAT", "")
            if not token:
                raise ValueError("Confluence Server/DC requires CONFLUENCE_PAT")
            auth = BearerAuth(token)

        return cls(
            base_url=base_url.rstrip("/"),
            deployment=deployment,
            space_keys=spaces,
            cql=cql,
            workers=workers,
            auth=auth,
        )


@dataclass(frozen=True)
class _Page:
    page_id: str
    title: str
    version: int
    updated_at: str


class _StorageTextParser(HTMLParser):
    _BLOCK_TAGS = {
        "ac:plain-text-body",
        "ac:rich-text-body",
        "address",
        "article",
        "blockquote",
        "br",
        "div",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "hr",
        "li",
        "ol",
        "p",
        "pre",
        "section",
        "table",
        "td",
        "th",
        "tr",
        "ul",
    }
    _SKIP_TAGS = {"script", "style"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1
        elif tag in self._BLOCK_TAGS:
            self._parts.append("\n")
        elif tag == "img":
            alt = dict(attrs).get("alt")
            if alt:
                self._parts.append(alt)

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
        elif tag in self._BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            self._parts.append(data)

    def text(self) -> str:
        return re.sub(r"[ \t]+", " ", "".join(self._parts)).strip()


def storage_to_text(storage_html: str) -> str:
    parser = _StorageTextParser()
    parser.feed(storage_html)
    return normalize(parser.text())


class ConfluenceSource:
    _CACHE_NAMESPACE = "confluence"

    def __init__(self, config: ConfluenceConfig) -> None:
        self._config = config

    def _client(self) -> httpx.Client:
        kwargs: dict = {
            "headers": {"Accept": "application/json"},
            "timeout": httpx.Timeout(30.0),
            "follow_redirects": True,
        }
        self._config.auth.apply(kwargs)
        return httpx.Client(**kwargs)

    def _url(self, path: str) -> str:
        base = self._config.base_url
        if self._config.deployment == "cloud" and base.endswith("/wiki"):
            base = base[:-5]
        return f"{base}{path}"

    def _get(self, client: httpx.Client, url: str, params: dict | None = None) -> dict:
        delay = 0.5
        for attempt in range(5):
            try:
                response = client.get(url, params=params)
            except httpx.RequestError:
                if attempt == 4:
                    raise
                time.sleep(delay)
                delay *= 2
                continue
            if response.status_code not in _RETRY_STATUSES:
                response.raise_for_status()
                return response.json()
            if attempt == 4:
                response.raise_for_status()
            retry_after = response.headers.get("Retry-After")
            time.sleep(float(retry_after) if retry_after else delay)
            delay *= 2
        raise RuntimeError("Confluence retry loop exhausted")

    def _paginate(self, client: httpx.Client, path: str, params: dict) -> list[dict]:
        results: list[dict] = []
        url = self._url(path)
        current_params: dict | None = dict(params)
        while url:
            data = self._get(client, url, current_params)
            page_results = data.get("results", [])
            results.extend(page_results)
            next_url = data.get("_links", {}).get("next")
            if next_url:
                url = urljoin(self._config.base_url + "/", next_url)
                current_params = None
            elif self._config.deployment == "server" and len(page_results) == data.get(
                "limit", 0
            ):
                current_params = dict(params)
                current_params["start"] = data.get("start", 0) + len(page_results)
            else:
                url = ""
        return results

    @staticmethod
    def _page_from_item(item: dict) -> _Page | None:
        content = item.get("content", item)
        if (
            content.get("type", "page") != "page"
            or content.get("status", "current") != "current"
        ):
            return None
        page_id = content.get("id")
        if not page_id:
            return None
        version = content.get("version", {})
        return _Page(
            page_id=str(page_id),
            title=content.get("title", str(page_id)),
            version=int(version.get("number", 0)),
            updated_at=version.get("createdAt") or version.get("when", ""),
        )

    def _discover_cloud(self, client: httpx.Client) -> list[_Page]:
        items: list[dict] = []
        if self._config.cql:
            items.extend(
                self._paginate(
                    client,
                    "/wiki/rest/api/search",
                    {"cql": self._config.cql, "limit": 100, "expand": "content.version"},
                )
            )
        for key in self._config.space_keys:
            spaces = self._paginate(
                client, "/wiki/api/v2/spaces", {"keys": key, "limit": 100}
            )
            if not spaces:
                logger.warning("Confluence space not found or inaccessible: {}", key)
                continue
            items.extend(
                self._paginate(
                    client,
                    "/wiki/api/v2/pages",
                    {"space-id": spaces[0]["id"], "status": "current", "limit": 100},
                )
            )
        return [page for item in items if (page := self._page_from_item(item))]

    def _discover_server(self, client: httpx.Client) -> list[_Page]:
        cql = self._config.cql
        if not cql:
            quoted = ",".join(f'"{key}"' for key in self._config.space_keys)
            cql = f"type=page and space in ({quoted})"
        items = self._paginate(
            client,
            "/rest/api/content/search",
            {"cql": cql, "limit": 100, "expand": "version"},
        )
        return [page for item in items if (page := self._page_from_item(item))]

    def _fetch_page(self, page: _Page) -> tuple[str, dict]:
        with self._client() as client:
            if self._config.deployment == "cloud":
                data = self._get(
                    client,
                    self._url(f"/wiki/api/v2/pages/{page.page_id}"),
                    {"body-format": "storage"},
                )
                storage = data.get("body", {}).get("storage", {}).get("value", "")
            else:
                data = self._get(
                    client,
                    self._url(f"/rest/api/content/{page.page_id}"),
                    {"expand": "body.storage,version"},
                )
                storage = data.get("body", {}).get("storage", {}).get("value", "")
            text = storage_to_text(storage)
            webui = data.get("_links", {}).get("webui", "")
            if self._config.deployment == "cloud":
                root = self._config.base_url.removesuffix("/wiki")
            else:
                root = self._config.base_url
            record = {
                "version": page.version,
                "updated_at": page.updated_at,
                "title": page.title,
                "content": text,
                "sha256": hashlib.sha256(text.encode()).hexdigest(),
                "url": urljoin(root + "/", webui.lstrip("/")) if webui else "",
            }
            return page.page_id, record

    def iter_documents(self, cache: EmbedCache | None = None) -> list[SourceDocument]:
        cached = cache.get_documents(self._CACHE_NAMESPACE) if cache else {}
        with self._client() as client:
            pages = (
                self._discover_cloud(client)
                if self._config.deployment == "cloud"
                else self._discover_server(client)
            )
        discovered = {page.page_id: page for page in pages}
        records: dict[str, dict] = {}
        changed: list[_Page] = []
        for page_id, page in discovered.items():
            old = cached.get(page_id)
            if (
                old
                and int(old.get("version", -1)) == page.version
                and old.get("content") is not None
            ):
                records[page_id] = old
            else:
                changed.append(page)

        if changed:
            logger.info(
                "Fetching {} changed Confluence pages with {} workers",
                len(changed),
                self._config.workers,
            )
            with ThreadPoolExecutor(max_workers=self._config.workers) as executor:
                futures = [executor.submit(self._fetch_page, page) for page in changed]
                for future in as_completed(futures):
                    page_id, record = future.result()
                    records[page_id] = record

        deleted = set(cached) - set(discovered)
        if deleted:
            logger.info("Reconciled {} deleted/archived Confluence pages", len(deleted))
        if cache:
            cache.replace_documents(self._CACHE_NAMESPACE, records)

        return [
            SourceDocument(
                text=record["content"],
                source=record["title"],
                metadata={
                    "source_type": "confluence",
                    "page_id": page_id,
                    "version": record["version"],
                    "url": record.get("url", ""),
                },
            )
            for page_id, record in sorted(records.items())
            if record.get("content", "").strip()
        ]
