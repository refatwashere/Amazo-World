import pytest

from amazo_bot.handlers.common import parse_referral_arg


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        ([], None),
        (["abc"], None),
        (["-2"], None),
        (["0"], None),
        (["123"], 123),
    ],
)
def test_parse_referral_arg(args: list[str], expected: int | None) -> None:
    assert parse_referral_arg(args) == expected

