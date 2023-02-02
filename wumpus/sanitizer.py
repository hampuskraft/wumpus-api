from pydantic import BaseModel, Field
from unidecode import unidecode


class Member(BaseModel):
    id: str
    username: str
    nickname: str | None
    roles: list[str] = Field(default_factory=list, max_items=250)


class SanitizeSchema(BaseModel):
    dehoist: bool = True
    exclude_roles: list[str] = Field(default_factory=list, max_items=250)
    exclude_users: list[str] = Field(default_factory=list, max_items=1000)
    fallback_name: str = Field(default="ZChange Name", min_length=1, max_length=32)
    force_username: bool = False
    max_consecutive: int = Field(default=0, ge=0, le=32)
    max_consecutive_upper: int = Field(default=0, ge=0, le=32)
    members: list[Member] = Field(min_items=1, max_items=1000)
    replace_char: str = Field(default="", max_length=1)


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

        if schema.force_username:
            name = member.username

        name = unidecode(name, errors="replace", replace_str=schema.replace_char)

        if schema.max_consecutive:
            name = Sanitizer.replace_consecutive(name, schema.max_consecutive)

        if schema.max_consecutive_upper:
            name = Sanitizer.replace_consecutive_upper(name, schema.max_consecutive_upper)

        if schema.dehoist:
            name = Sanitizer.dehoist(name)

        name = " ".join(name.split())
        name = name[:32]

        if not name:
            name = schema.fallback_name

        return name

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
