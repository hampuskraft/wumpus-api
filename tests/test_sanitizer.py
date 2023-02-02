from wumpus.sanitizer import Member, Sanitizer, SanitizeSchema


def test_replace_consecutive() -> None:
    assert Sanitizer.replace_consecutive("aaabbbccc", 1) == "abc"
    assert Sanitizer.replace_consecutive("aaabbbccc", 2) == "aabbcc"
    assert Sanitizer.replace_consecutive("aaabbbccc", 3) == "aaabbbccc"


def test_replace_consecutive_upper() -> None:
    assert Sanitizer.replace_consecutive_upper("TEST", 1) == "test"
    assert Sanitizer.replace_consecutive_upper("TEST", 2) == "test"
    assert Sanitizer.replace_consecutive_upper("TEST", 3) == "test"
    assert Sanitizer.replace_consecutive_upper("TEST", 4) == "test"
    assert Sanitizer.replace_consecutive_upper("test", 4) == "test"
    assert Sanitizer.replace_consecutive_upper("Test Test Test", 2) == "Test Test Test"


def test_dehoist() -> None:
    assert Sanitizer.dehoist("!@#$%^&*()_+{}|:<>?") == ""
    assert Sanitizer.dehoist("!@#$%^&*()_+{}|:<>?abc") == "abc"
    assert Sanitizer.dehoist("abc!@#$%^&*()_+{}|:<>?") == "abc!@#$%^&*()_+{}|:<>?"
    assert Sanitizer.dehoist("abc") == "abc"


def test_sanitize_member() -> None:
    member = Member(
        id="123",
        username="test",
        nickname="test",
        roles=[],
    )
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "test"

    member = Member(
        id="123",
        username="testabc",
        nickname="test",
        roles=["123"],
    )
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], force_username=True)) == "testabc"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], force_username=False)) == "test"
    assert (
        Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], force_username=True, exclude_roles=["123"]))
        == "test"
    )

    member = Member(
        id="123",
        username="𝗨𝗻𝗸𝗻𝗼𝘄𝗻 𝗚𝗼𝗱 𝗣𝗹𝗮𝘆𝗲𝗿",
        nickname=None,
        roles=[],
    )
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "Unknown God Player"

    member = Member(
        id="123",
        username="A1denxX",
        nickname=".𝒶𝒾𝒹ℯ𝓃",
        roles=[],
    )
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "aiden"

    member = Member(
        id="123",
        username="test",
        nickname="!!!𝓡𝓮𝓮𝓮𝓮𝓮𝓮𝓮𝓮𝓮𝓮 😎",
        roles=[],
    )
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_consecutive=4)) == "Reeee"
