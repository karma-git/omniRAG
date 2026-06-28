"""Unit tests for Telegram markdown → HTML converter."""

from app.channels.telegram import _md_to_tg_html


def test_bold() -> None:
    assert "<b>hello</b>" in _md_to_tg_html("**hello**")


def test_italic() -> None:
    assert "<i>world</i>" in _md_to_tg_html("*world*")


def test_inline_code() -> None:
    result = _md_to_tg_html("run `pip install uv` now")
    assert "<code>pip install uv</code>" in result


def test_header_becomes_bold() -> None:
    result = _md_to_tg_html("# My Title")
    assert "<b>My Title</b>" in result


def test_h2_becomes_bold() -> None:
    result = _md_to_tg_html("## Section")
    assert "<b>Section</b>" in result


def test_list_items_become_bullets() -> None:
    result = _md_to_tg_html("- first\n- second")
    assert "• first" in result
    assert "• second" in result


def test_code_block_no_lang() -> None:
    result = _md_to_tg_html("```\nsome code\n```")
    assert "<pre>" in result
    assert "<code>" in result
    assert "some code" in result


def test_code_block_with_lang() -> None:
    result = _md_to_tg_html("```python\nprint('hi')\n```")
    assert "language-python" in result
    assert "print" in result


def test_html_special_chars_escaped() -> None:
    result = _md_to_tg_html("use <b> and & in text")
    assert "&lt;b&gt;" in result
    assert "&amp;" in result


def test_code_content_not_double_escaped() -> None:
    result = _md_to_tg_html("`a < b`")
    assert "<code>" in result
    assert "a &lt; b" in result


def test_plain_text_passthrough() -> None:
    result = _md_to_tg_html("Hello world, no markdown here.")
    assert "Hello world, no markdown here." in result


def test_mixed_formatting() -> None:
    text = "## Title\n\n**bold** and `code`\n\n```yaml\nkey: value\n```"
    result = _md_to_tg_html(text)
    assert "<b>Title</b>" in result
    assert "<b>bold</b>" in result
    assert "<code>code</code>" in result
    assert "language-yaml" in result
    assert "key: value" in result
