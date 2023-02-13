from wumpus.sanitizer import Member, Sanitizer, SanitizeSchema


def test_get_leading_emoji() -> None:
    assert Sanitizer.get_leading_emoji("", 1) == ""
    assert Sanitizer.get_leading_emoji("abc", 1) == ""
    assert Sanitizer.get_leading_emoji("👀abc", 1) == "👀"
    assert Sanitizer.get_leading_emoji("👀👀abc", 1) == "👀"
    assert Sanitizer.get_leading_emoji("👀👀abc", 2) == "👀👀"
    assert Sanitizer.get_leading_emoji("👀👀👀abc", 2) == "👀👀"
    assert Sanitizer.get_leading_emoji("👀👀👀abc", 3) == "👀👀👀"


def test_get_trailing_emoji() -> None:
    assert Sanitizer.get_trailing_emoji("", 1) == ""
    assert Sanitizer.get_trailing_emoji("abc", 1) == ""
    assert Sanitizer.get_trailing_emoji("abc👀", 1) == "👀"
    assert Sanitizer.get_trailing_emoji("abc👀👀", 1) == "👀"
    assert Sanitizer.get_trailing_emoji("abc👀👀", 2) == "👀👀"
    assert Sanitizer.get_trailing_emoji("abc👀👀👀", 2) == "👀👀"
    assert Sanitizer.get_trailing_emoji("abc👀👀👀", 3) == "👀👀👀"


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

    member = Member(id="123", username="𝗨𝗻𝗸𝗻𝗼𝘄𝗻 𝗚𝗼𝗱 𝗣𝗹𝗮𝘆𝗲𝗿", nickname=None, roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "Unknown God Player"

    member = Member(id="123", username="A1denxX", nickname=".𝒶𝒾𝒹ℯ𝓃", roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "aiden"

    member = Member(id="123", username="test", nickname="!!!𝓡𝓮𝓮𝓮𝓮𝓮𝓮𝓮𝓮𝓮𝓮 😎", roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_consecutive=4)) == "Reeee"

    member = Member(id="123", username="test", nickname="👀👀👀test👀👀👀", roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "test"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_emoji_leading=1)) == "👀 test"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_emoji_trailing=1)) == "test 👀"
    assert (
        Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_emoji_leading=1, max_emoji_trailing=1))
        == "👀 test 👀"
    )
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_emoji_leading=2)) == "👀👀 test"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_emoji_trailing=2)) == "test 👀👀"
    assert (
        Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_emoji_leading=2, max_emoji_trailing=2))
        == "👀👀 test 👀👀"
    )

    member = Member(id="123", username="█▀█ █▄█ ▀█▀", nickname="ZChange Name", roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "ZChange Name"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], strict=True)) == "ZChange Name"

    member = Member(id="123", username="test", nickname="ZChange Name", roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "test"

    member = Member(id="123", username="🅕🅞🅡🅜🅤🅛🅐🅢🅤🅜🅞", nickname=None, roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "FORMULASUMO"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_consecutive_upper=4)) == "formulasumo"

    member = Member(id="123", username="|| C O N Q U E S T O R || ®", nickname=None, roles=[])
    assert (
        Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_char_spacing=4, max_consecutive_upper=4))
        == "conquestor®"
    )

    member = Member(id="123", username="Vitor-Yato Sykrony®", nickname=None, roles=[])
    assert (
        Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], max_char_spacing=4, max_consecutive_upper=4))
        == "Vitor-Yato Sykrony®"
    )

    member = Member(id="123", username="test®", nickname=None, roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], trailing_trademark=True)) == "test®"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], trailing_trademark=False)) == "test"
    assert (
        Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], trailing_trademark=True, strict=True))
        == "test®"
    )

    member = Member(id="123", username="test", nickname="test™", roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], trailing_trademark=True)) == "test™"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], trailing_trademark=False)) == "test"
    assert (
        Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], trailing_trademark=True, strict=True))
        == "test™"
    )

    member = Member(id="123", username="🆂🅰🅽🆈🅰", nickname=None, roles=[])
    assert (
        Sanitizer.sanitize_member(
            member,
            SanitizeSchema(
                members=[member],
                max_char_spacing=3,
                max_consecutive=4,
                max_consecutive_upper=4,
                max_emoji_leading=1,
                max_emoji_trailing=1,
            ),
        )
        == "sanya"
    )

    member = Member(id="123", username="WG 丶↘☣DÊÂD PÔÔL☣↙", nickname=None, roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "WG Zhu \DEAD POOL/"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], strict=True)) == "WG Zhu DEAD POOL"

    member = Member(id="123", username="WG 丶↘☣DÊÂD PÔÔL☣↙", nickname="WG Zhu \DEAD POOL/", roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "WG Zhu \DEAD POOL/"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], strict=True)) == "WG Zhu DEAD POOL"

    member = Member(id="123", username="『Ézz ↯ R È H Û 』", nickname=None, roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "Ezz | R E H U"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], strict=True)) == "Ezz R E H U"

    member = Member(id="123", username="[ ಥ‿ಥ ] S A D", nickname=None, roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "th_th S A D"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], strict=True)) == "th_th S A D"

    member = Member(id="123", username="__test-123__", nickname=None, roles=[])
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member])) == "test-123__"
    assert Sanitizer.sanitize_member(member, SanitizeSchema(members=[member], strict=True)) == "test-123"
