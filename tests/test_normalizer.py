"""Tests for app/core/normalizer.py."""

from app.core.normalizer import normalize


def test_yaml_frontmatter_stripped() -> None:
    text = "---\ntitle: Test\nauthor: me\n---\nHello world"
    assert normalize(text) == "Hello world"


def test_toml_frontmatter_stripped() -> None:
    text = "+++\ntitle = 'Test'\n+++\nHello world"
    assert normalize(text) == "Hello world"


def test_links_unwrapped() -> None:
    assert normalize("[click here](https://example.com)") == "click here"


def test_images_become_alt_text() -> None:
    assert normalize("![company logo](img/logo.png)") == "company logo"


def test_image_no_alt_removed() -> None:
    assert normalize("![](img/logo.png)") == ""


def test_bold_star_stripped() -> None:
    assert normalize("This is **important** text") == "This is important text"


def test_bold_underscore_stripped() -> None:
    assert normalize("This is __important__ text") == "This is important text"


def test_italic_stripped() -> None:
    assert normalize("This is *emphasized* text") == "This is emphasized text"


def test_strikethrough_stripped() -> None:
    assert normalize("~~deprecated feature~~") == "deprecated feature"


def test_headers_stripped() -> None:
    text = "## Section Title\nSome text below"
    assert normalize(text) == "Section Title\nSome text below"


def test_all_header_levels() -> None:
    for level in range(1, 7):
        text = f"{'#' * level} Title"
        assert normalize(text) == "Title"


def test_table_converted_to_csv() -> None:
    text = "| Name | Age |\n| --- | --- |\n| Alice | 30 |\n| Bob | 25 |"
    result = normalize(text)
    assert "Name, Age" in result
    assert "Alice, 30" in result
    assert "Bob, 25" in result
    assert "---" not in result
    assert "|" not in result


def test_code_fence_markers_stripped_content_kept() -> None:
    text = "```python\nprint('hello')\n```"
    result = normalize(text)
    assert "```" not in result
    assert "print('hello')" in result


def test_multiple_blank_lines_collapsed() -> None:
    text = "paragraph one\n\n\n\nparagraph two"
    assert normalize(text) == "paragraph one\n\nparagraph two"


def test_mixed_formatting() -> None:
    text = "## About\nThis is **bold** and [a link](https://x.com)."
    assert normalize(text) == "About\nThis is bold and a link."


def test_empty_string() -> None:
    assert normalize("") == ""


def test_plain_text_unchanged() -> None:
    text = "Plain text with no markdown formatting at all."
    assert normalize(text) == text
