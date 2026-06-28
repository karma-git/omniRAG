from __future__ import annotations

import re

_FRONTMATTER = re.compile(r"^(?:---|\+\+\+)\n.*?\n(?:---|\+\+\+)\s*\n?", re.DOTALL)
_CODE_FENCE = re.compile(r"^```[^\n]*$", re.MULTILINE)
_IMAGE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")
_BOLD_STAR = re.compile(r"\*\*([^*\n]+)\*\*")
_BOLD_UNDER = re.compile(r"__([^_\n]+)__")
_ITALIC_STAR = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_STRIKE = re.compile(r"~~([^~\n]+)~~")
_HEADER = re.compile(r"^#{1,6}\s+", re.MULTILINE)
_TABLE_SEP = re.compile(r"^\|[\s|:=-]+\|$")
_TABLE_ROW = re.compile(r"^\|(.+)\|$")
_MULTI_BLANK = re.compile(r"\n{3,}")
_TRAIL_WS = re.compile(r"[ \t]+$", re.MULTILINE)


def normalize(text: str) -> str:
    """Strip markdown noise to produce clean plain text for embedding."""
    text = _strip_frontmatter(text)
    text = _CODE_FENCE.sub("", text)  # remove ``` markers, keep code content
    text = _IMAGE.sub(r"\1", text)  # ![alt](url) → alt
    text = _LINK.sub(r"\1", text)  # [text](url) → text
    text = _BOLD_STAR.sub(r"\1", text)  # **bold** → bold
    text = _BOLD_UNDER.sub(r"\1", text)  # __bold__ → bold
    text = _ITALIC_STAR.sub(r"\1", text)  # *italic* → italic
    text = _STRIKE.sub(r"\1", text)  # ~~strike~~ → strike
    text = _HEADER.sub("", text)  # ## Title → Title
    text = _convert_tables(text)
    text = _TRAIL_WS.sub("", text)
    text = _MULTI_BLANK.sub("\n\n", text)
    return text.strip()


def _strip_frontmatter(text: str) -> str:
    m = _FRONTMATTER.match(text)
    return text[m.end() :] if m else text


def _convert_tables(text: str) -> str:
    """Convert markdown table rows to comma-separated values; drop separator rows."""
    lines = text.splitlines()
    out: list[str] = []
    for line in lines:
        s = line.strip()
        if _TABLE_SEP.match(s):
            continue
        m = _TABLE_ROW.match(s)
        if m:
            cells = [c.strip() for c in m.group(1).split("|") if c.strip()]
            out.append(", ".join(cells))
        else:
            out.append(line)
    return "\n".join(out)
