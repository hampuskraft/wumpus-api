import re

import emoji
from pydantic import BaseModel, Field
from unidecode import unidecode

C = "©"
R = "®"
TM = "™"
HEART = "<3"

REGIONAL_INDICATORS_TO_ASCII = {
    "🇦": "A",
    "🇧": "B",
    "🇨": "C",
    "🇩": "D",
    "🇪": "E",
    "🇫": "F",
    "🇬": "G",
    "🇭": "H",
    "🇮": "I",
    "🇯": "J",
    "🇰": "K",
    "🇱": "L",
    "🇲": "M",
    "🇳": "N",
    "🇴": "O",
    "🇵": "P",
    "🇶": "Q",
    "🇷": "R",
    "🇸": "S",
    "🇹": "T",
    "🇺": "U",
    "🇻": "V",
    "🇼": "W",
    "🇽": "X",
    "🇾": "Y",
    "🇿": "Z",
    "🅰": "A",
    "🅱": "B",
    "🅾": "O",
    "🅿": "P",
}

STRICT_REGEX = re.compile(r"[^\w &'.-]", re.ASCII)
STRICT_SPECIAL_CHARS = {" ", "_", ".", "-", "&", "'"}

BRACKETS_REGEX = re.compile(r"(\(|\[|\{)(\w)(\)|\]|\})")
BRACKETS_MAPPING = {")": "(", "]": "[", "}": "{"}


class Member(BaseModel):
    id: str
    username: str
    nickname: str | None
    roles: list[str] = Field(default_factory=list, max_items=250)
    force_username: bool = False


class SanitizeSchema(BaseModel):
    dehoist: bool = True
    exclude_roles: list[str] = Field(default_factory=list, max_items=250)
    exclude_users: list[str] = Field(default_factory=list, max_items=1000)
    fallback_name: str = Field(default="ZChange Name", min_length=1, max_length=32)
    force_username: bool = False
    max_char_spacing: int = Field(default=0, ge=0, le=32)
    max_consecutive: int = Field(default=0, ge=0, le=32)
    max_consecutive_upper: int = Field(default=0, ge=0, le=32)
    max_emoji_leading: int = Field(default=0, ge=0, le=32)
    max_emoji_trailing: int = Field(default=0, ge=0, le=32)
    max_spaces: int = Field(default=0, ge=0, le=32)
    members: list[Member] = Field(min_items=1, max_items=1000)
    normalize_brackets: bool = True
    normalize_regional: bool = True
    replace_char: str = Field(default="", max_length=1)
    strict: bool = False
    strip_pipes_leading: bool = True
    strip_pipes_trailing: bool = True
    trailing_heart: bool = True
    trailing_trademark: bool = False


class Sanitizer:
    @staticmethod
    def sanitize(schema: SanitizeSchema) -> dict[str, str]:
        return {member.id: Sanitizer.sanitize_member(member, schema) for member in schema.members}

    @staticmethod
    def sanitize_member(member: Member, schema: SanitizeSchema) -> str:
        name = member.nickname or member.username

        if member.id in schema.exclude_users:
            return name

        if any(role in member.roles for role in schema.exclude_roles):
            return name

        if schema.force_username or member.force_username or schema.fallback_name == name:
            name = member.username

        if schema.normalize_regional:
            name = "".join(REGIONAL_INDICATORS_TO_ASCII.get(c, c) for c in name)

        trailing_trademark = ""
        if schema.trailing_trademark:
            trailing_trademark = R if name.endswith(R) else TM if name.endswith(TM) else ""

        name = name.replace(C, "").replace(R, "").replace(TM, "")

        leading_emoji = ""
        trailing_emoji = ""

        if schema.max_emoji_leading:
            leading_emoji = Sanitizer.get_leading_emoji(name, schema.max_emoji_leading)

        if schema.max_emoji_trailing:
            trailing_emoji = Sanitizer.get_trailing_emoji(name, schema.max_emoji_trailing)

        name = unidecode(name, errors="replace", replace_str=schema.replace_char)
        name = " ".join(name.split())

        trailing_heart = name.endswith(HEART)
        if schema.trailing_heart:
            name = name.replace(HEART, "")

        if schema.normalize_brackets:
            name = Sanitizer.normalize_brackets(name)

        if schema.dehoist:
            name = Sanitizer.dehoist(name)

        if schema.max_spaces:
            name = Sanitizer.replace_spaces(name, schema.max_spaces)

        if schema.max_char_spacing:
            name = Sanitizer.replace_char_spacing(name, schema.max_char_spacing)

        if schema.max_consecutive:
            name = Sanitizer.replace_consecutive(name, schema.max_consecutive)

        if schema.max_consecutive_upper:
            name = Sanitizer.replace_consecutive_upper(name, schema.max_consecutive_upper)

        if schema.strip_pipes_leading:
            name = name.lstrip("|")

        if schema.strip_pipes_trailing:
            name = name.rstrip("|")

        if schema.normalize_brackets:
            name = Sanitizer.strip_dangling_brackets(name)

        if schema.strict:
            name = re.sub(STRICT_REGEX, "", name).strip("".join(STRICT_SPECIAL_CHARS))

        if trailing_trademark:
            name = f"{name}{trailing_trademark}"

        if leading_emoji:
            name = f"{leading_emoji} {name}"

        if trailing_emoji:
            name = f"{name} {trailing_emoji}"

        if schema.trailing_heart and trailing_heart:
            name = f"{name} {HEART}"

        name = " ".join(name.split())[:32]

        if all(emoji.is_emoji(char) for char in name.split()):
            name = schema.fallback_name

        if not name:
            name = schema.fallback_name

        return name

    @staticmethod
    def get_leading_emoji(name: str, max_leading_emoji: int) -> str:
        """
        Get the leading emoji from a name.
        """

        leading_emojis = []

        for char in name:
            if emoji.is_emoji(char):
                leading_emojis.append(char)
            else:
                break

        if len(leading_emojis) > max_leading_emoji:
            leading_emojis = leading_emojis[:max_leading_emoji]

        return "".join(leading_emojis)

    @staticmethod
    def get_trailing_emoji(name: str, max_trailing_emoji: int) -> str:
        """
        Get the trailing emoji from a name.
        """

        trailing_emojis = []

        for char in reversed(name):
            if emoji.is_emoji(char):
                trailing_emojis.append(char)
            else:
                break

        if len(trailing_emojis) > max_trailing_emoji:
            trailing_emojis = trailing_emojis[:max_trailing_emoji]

        return "".join(reversed(trailing_emojis))

    @staticmethod
    def replace_spaces(name: str, max_spaces: int) -> str:
        """
        If the number of spaces in a name is >= `max_spaces`, remove all spaces.
        """

        if name.count(" ") >= max_spaces:
            name = name.replace(" ", "")

        return name

    @staticmethod
    def replace_char_spacing(name: str, max_char_spacing: int) -> str:
        """
        Join any single-character words together if the count is >= `max_char_spacing`.
        """

        name_split = name.strip().split()
        single_char_words = [word for word in name_split if len(word) == 1]

        if len(single_char_words) > max_char_spacing:
            return "".join(single_char_words) + " ".join(word for word in name_split if len(word) > 1)
        else:
            return " ".join(name_split)

    @staticmethod
    def replace_consecutive(name: str, max_consecutive: int) -> str:
        """
        Collapse any consecutive characters into a single character.
        """

        consecutive = 0
        last_char = None
        new_name = ""

        for char in name:
            if char == last_char:
                consecutive += 1
            else:
                consecutive = 1

            if consecutive <= max_consecutive:
                new_name += char

            last_char = char

        return new_name

    @staticmethod
    def replace_consecutive_upper(name: str, max_consecutive_upper: int) -> str:
        """
        Convert name to lowercase if the number of uppercase characters >= `max_consecutive_upper`.
        """

        consecutive = 0
        new_name = ""

        for char in name:
            if char.isupper():
                consecutive += 1
            else:
                consecutive = 0

            if consecutive >= max_consecutive_upper:
                new_name = name.lower()
                break
            else:
                new_name += char

        return new_name

    @staticmethod
    def dehoist(name: str) -> str:
        """
        Dehoist a name by stripping any leading non-alphanumeric characters.
        """

        for char in name:
            if char.isalnum():
                break
            else:
                name = name[1:]

        return name

    @staticmethod
    def normalize_brackets(name: str) -> str:
        """
        Remove parentheses (), square brackets [], or curly brackets {} around single characters.
        """

        matches = re.findall(BRACKETS_REGEX, name)
        for match in matches:
            name = name.replace("".join(match), match[1])

        return name

    @staticmethod
    def strip_dangling_brackets(name: str) -> str:
        """
        Remove dangling parentheses (), square brackets [], or curly brackets {} (e.g. "foo (bar" -> "foo bar").
        """

        stack = []

        for char in name:
            if char in BRACKETS_MAPPING.values():
                stack.append(char)
            elif char in BRACKETS_MAPPING.keys():
                if not stack or stack[-1] != BRACKETS_MAPPING[char]:
                    name = name.replace(char, "")
                else:
                    stack.pop()

        while stack:
            name = name.replace(stack.pop(), "")

        return name.replace("()", "").replace("[]", "").replace("{}", "")
