import re

import emoji
from pydantic import BaseModel, Field
from unidecode import unidecode

R = "®"
TM = "™"


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
    normalize_parentheses: bool = True
    replace_char: str = Field(default="", max_length=1)
    strip_pipes: bool = True
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

        if schema.strip_pipes:
            name = name.replace("|", "")

        trailing_trademark = ""
        if schema.trailing_trademark:
            trailing_trademark = R if name.endswith(R) else TM if name.endswith(TM) else ""

        name = name.replace(R, "").replace(TM, "")

        leading_emoji = ""
        trailing_emoji = ""

        if schema.max_emoji_leading:
            leading_emoji = Sanitizer.get_leading_emoji(name, schema.max_emoji_leading)

        if schema.max_emoji_trailing:
            trailing_emoji = Sanitizer.get_trailing_emoji(name, schema.max_emoji_trailing)

        name = unidecode(name, errors="replace", replace_str=schema.replace_char)
        name = " ".join(name.split())

        if schema.normalize_parentheses:
            name = Sanitizer.normalize_parentheses(name)

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

        if trailing_trademark:
            name = f"{name}{trailing_trademark}"

        if leading_emoji:
            name = f"{leading_emoji} {name}"

        if trailing_emoji:
            name = f"{name} {trailing_emoji}"

        name = name[:32]
        if not name or all(emoji.is_emoji(char) for char in name.split()):
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
    def normalize_parentheses(name: str) -> str:
        """
        Remove parentheses or square brackets around single characters.
        """

        matches = re.findall(r"\((\w)\)", name)
        for match in matches:
            name = name.replace(f"({match})", match)

        matches = re.findall(r"\[(\w)\]", name)
        for match in matches:
            name = name.replace(f"[{match}]", match)

        return name
