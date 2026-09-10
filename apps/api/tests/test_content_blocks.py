"""The editorial boundary only accepts safe, bounded semantic records."""

import pytest
from pydantic import ValidationError

from app.schemas import ContentBlock, Page


@pytest.mark.parametrize(
    "href",
    ["javascript:alert(1)", "//attacker.invalid", "data:text/html,test", "/\\attacker.invalid"],
)
def test_unsafe_content_links_rejected(href):
    with pytest.raises(ValidationError):
        ContentBlock(kind="link", href=href)


def test_editorial_scripts_and_external_image_paths_rejected():
    with pytest.raises(ValidationError):
        ContentBlock(kind="text", text="copy", script="alert(1)")
    with pytest.raises(ValidationError):
        ContentBlock(kind="image", image="https://attacker.invalid/image.png")


def test_page_tree_depth_is_bounded():
    block = {"kind": "text", "text": "copy"}
    for _ in range(17):
        block = {"kind": "group", "children": [block]}
    with pytest.raises(ValidationError):
        Page(
            slug="example",
            title="Example",
            description="Example",
            heading="Example",
            intro="Example",
            blocks=[block],
        )
