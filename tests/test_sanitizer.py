from wumpus.sanitizer import Member, Sanitizer, SanitizeSchema


def test_get_leading_emoji() -> None:
    assert Sanitizer.get_leading_emoji("", 1) == ""
    assert Sanitizer.get_leading_emoji("abc", 1) == ""
    assert Sanitizer.get_leading_emoji("ðabc", 1) == "ð"
    assert Sanitizer.get_leading_emoji("ððabc", 1) == "ð"
    assert Sanitizer.get_leading_emoji("ððabc", 2) == "ðð"
    assert Sanitizer.get_leading_emoji("ðððabc", 2) == "ðð"
    assert Sanitizer.get_leading_emoji("ðððabc", 3) == "ððð"


def test_get_trailing_emoji() -> None:
    assert Sanitizer.get_trailing_emoji("", 1) == ""
    assert Sanitizer.get_trailing_emoji("abc", 1) == ""
    assert Sanitizer.get_trailing_emoji("abcð", 1) == "ð"
    assert Sanitizer.get_trailing_emoji("abcðð", 1) == "ð"
    assert Sanitizer.get_trailing_emoji("abcðð", 2) == "ðð"
    assert Sanitizer.get_trailing_emoji("abcððð", 2) == "ðð"
    assert Sanitizer.get_trailing_emoji("abcððð", 3) == "ððð"


def test_replace_char_spacing() -> None:
    assert Sanitizer.replace_char_spacing("a b c", 2) == "abc"
    assert Sanitizer.replace_char_spacing("a b c", 3) == "a b c"
    assert Sanitizer.replace_char_spacing("aa bb cc", 2) == "aa bb cc"
    assert Sanitizer.replace_char_spacing("aa bb cc", 3) == "aa bb cc"
    assert Sanitizer.replace_char_spacing("J U S T I N", 5) == "JUSTIN"
    assert Sanitizer.replace_char_spacing("J U S T I N", 6) == "J U S T I N"


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


def test_normalize_brackets() -> None:
    assert Sanitizer.normalize_brackets("abc") == "abc"
    assert Sanitizer.normalize_brackets("(a)(b)(c)") == "abc"
    assert Sanitizer.normalize_brackets("(abc)(def)(ghi)") == "(abc)(def)(ghi)"
    assert Sanitizer.normalize_brackets("(abc) (def) (ghi)") == "(abc) (def) (ghi)"
    assert Sanitizer.normalize_brackets("[a][b][c]") == "abc"
    assert Sanitizer.normalize_brackets("[abc][def][ghi]") == "[abc][def][ghi]"
    assert Sanitizer.normalize_brackets("[abc] [def] [ghi]") == "[abc] [def] [ghi]"
    assert Sanitizer.normalize_brackets("{a}{b}{c}") == "abc"
    assert Sanitizer.normalize_brackets("{abc}{def}{ghi}") == "{abc}{def}{ghi}"
    assert Sanitizer.normalize_brackets("{abc} {def} {ghi}") == "{abc} {def} {ghi}"


def test_strip_dangling_brackets() -> None:
    assert Sanitizer.strip_dangling_brackets("()test test") == "test test"
    assert Sanitizer.strip_dangling_brackets("test (test") == "test test"
    assert Sanitizer.strip_dangling_brackets("test )test") == "test test"
    assert Sanitizer.strip_dangling_brackets("test test()") == "test test"


def test_sanitize_member() -> None:
    member = Member(id="123", username="test", nickname="test", roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "test"

    member = Member(id="123", username="testabc", nickname="test", roles=["123"])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], force_username=True)) == "testabc"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], force_username=False)) == "test"
    assert (
        Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], force_username=True, exclude_roles=["123"]))
        == "test"
    )

    member = Member(id="123", username="ð¨ð»ð¸ð»ð¼ðð» ðð¼ð± ð£ð¹ð®ðð²ð¿", nickname=None, roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "Unknown God Player"

    member = Member(id="123", username="A1denxX", nickname=".ð¶ð¾ð¹â¯ð", roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "aiden"

    member = Member(id="123", username="test", nickname="!!!ð¡ð®ð®ð®ð®ð®ð®ð®ð®ð®ð® ð", roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_consecutive=4)) == "Reeee"

    member = Member(id="123", username="test", nickname="ðððtestððð", roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "test"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_emoji_leading=1)) == "ð test"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_emoji_trailing=1)) == "test ð"
    assert (
        Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_emoji_leading=1, max_emoji_trailing=1))
        == "ð test ð"
    )
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_emoji_leading=2)) == "ðð test"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_emoji_trailing=2)) == "test ðð"
    assert (
        Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_emoji_leading=2, max_emoji_trailing=2))
        == "ðð test ðð"
    )

    member = Member(id="123", username="âââ âââ âââ", nickname="ZChange Name", roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "ZChange Name"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], strict=True)) == "ZChange Name"

    member = Member(id="123", username="test", nickname="ZChange Name", roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "test"

    member = Member(id="123", username="ððð¡ðð¤ððð¢ð¤ðð", nickname=None, roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "FORMULASUMO"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_consecutive_upper=4)) == "formulasumo"

    member = Member(id="123", username="|| C O N Q U E S T O R || Â®", nickname=None, roles=[])
    assert (
        Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_char_spacing=4, max_consecutive_upper=4))
        == "conquestor"
    )

    member = Member(id="123", username="Vitor-Yato SykronyÂ®", nickname=None, roles=[])
    assert (
        Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_char_spacing=4, max_consecutive_upper=4))
        == "Vitor-Yato Sykrony"
    )

    member = Member(id="123", username="testÂ®", nickname=None, roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], trailing_trademark=True)) == "testÂ®"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], trailing_trademark=False)) == "test"
    assert (
        Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], trailing_trademark=True, strict=True))
        == "testÂ®"
    )

    member = Member(id="123", username="test", nickname="testâ¢", roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], trailing_trademark=True)) == "testâ¢"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], trailing_trademark=False)) == "test"
    assert (
        Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], trailing_trademark=True, strict=True))
        == "testâ¢"
    )

    member = Member(id="123", username="Rem_yuzukiÂ©", nickname=None, roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(strict=True, members=[member])) == "Rem_yuzuki"

    member = Member(id="123", username="ðð°ð½ðð°", nickname=None, roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_consecutive_upper=4)) == "sanya"

    member = Member(id="123", username="WG ä¸¶ââ£DÃÃD PÃÃLâ£â", nickname=None, roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "WG Zhu \DEAD POOL/"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], strict=True)) == "WG Zhu DEAD POOL"

    member = Member(id="123", username="WG ä¸¶ââ£DÃÃD PÃÃLâ£â", nickname="WG Zhu \DEAD POOL/", roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "WG Zhu \DEAD POOL/"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], strict=True)) == "WG Zhu DEAD POOL"

    member = Member(id="123", username="ãÃzz â¯ R Ã H Ã ã", nickname=None, roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "Ezz | R E H U"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], strict=True)) == "Ezz R E H U"

    member = Member(id="123", username="[ à²¥â¿à²¥ ] S A D", nickname=None, roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "th_th S A D"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], strict=True)) == "th_th S A D"

    member = Member(id="123", username="__test-123&-.abc__&'_.!", nickname=None, roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "test-123&-.abc__&'_.!"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], strict=True)) == "test-123&-.abc"

    member = Member(id="123", username="test <3", nickname=None, roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "test <3"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], strict=True)) == "test <3"
    assert (
        Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], strict=True, trailing_heart=False))
        == "test 3"
    )

    member = Member(id="123", username="test 123", nickname=None, roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "test 123"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], strict=True)) == "test 123"
    assert (
        Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], strict=True, trailing_heart=False))
        == "test 123"
    )
