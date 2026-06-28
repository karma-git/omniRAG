from __future__ import annotations

import json

from loguru import logger
from openai import OpenAI

_SYSTEM = (
    "You extract atomic propositions from text. "
    "Each proposition is a single, self-contained factual statement "
    "that includes all context needed to understand it without reading the original. "
    'Respond with JSON only: {"propositions": ["...", "..."]}'
)

_USER = """\
Extract atomic propositions from the following text.
Each proposition must be a complete standalone sentence — \
no pronouns without antecedents, no implied context.

TEXT:
{text}"""


def extract_propositions(text: str, client: OpenAI, model: str) -> list[str]:
    """Break a chunk into atomic, self-contained factual statements via LLM.

    Falls back to returning the original chunk as a single proposition on any error.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": _USER.format(text=text)},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        content = response.choices[0].message.content or ""
        data = json.loads(content)
        props = data.get("propositions", [])
        valid = [p for p in props if isinstance(p, str) and p.strip()]
        if valid:
            return valid
        logger.warning("LLM returned empty propositions list — falling back to raw chunk")
    except Exception as exc:
        logger.warning("Proposition extraction failed ({}), using raw chunk", exc)
    return [text]
