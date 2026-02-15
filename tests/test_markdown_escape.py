from bot import escape_markdown_v2, format_lift_payload


def test_escape_markdown_v2_escapes_all_special_characters():
    specials = "_*[]()~`>#+-=|{}.!"
    escaped = escape_markdown_v2(specials)

    for char in specials:
        assert f"\\{char}" in escaped


def test_format_lift_payload_preserves_line_breaks_with_markdownv2_safe_newlines():
    payload = format_lift_payload("Line 1\nLine 2")
    assert payload == "Line 1  \nLine 2"

