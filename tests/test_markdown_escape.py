from amazo_bot.handlers.common import escape_markdown_text


def test_escape_markdown_text_escapes_reserved_chars() -> None:
    raw = "user_name [test](x)!"
    escaped = escape_markdown_text(raw)
    assert escaped == "user\\_name \\[test\\]\\(x\\)\\!"

