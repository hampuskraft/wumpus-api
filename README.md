# Wumpus API

Discord member username & nickname sanitization API. A hosted version is available at https://api.wump.io/v1.

> Used in production at [NetherGames Network](https://discord.gg/ng) with over 31,000 members.

## API Endpoints

### `POST /sanitize`

Produces a key-value map of member IDs → sanitized names.

#### Sanitization Rules

Sanitization is performed in the following order:

- Get the member's name (nickname or username).
- If the member ID is in `exclude_users`, skip sanitization.
- If the member has any roles specified in `exclude_roles`, skip sanitization.
- If `force_username` is true or the `name` is `fallback_name`, use the username.
- Store the leading & trailing emoji characters, limited to `max_emoji_leading` and `max_emoji_trailing`.
- Run [Unidecode](https://pypi.org/project/Unidecode/) on the `name` to convert Unicode characters to ASCII equivalents.
- If a character has no ASCII equivalent, replace it with the character specified in `replace_char`.
- Strip any leading, trailing, or consecutive whitespace from the name.
- Remove all spaces from the name if the number of spaces >= `max_spaces`.
- Join any single-character words together if the count is >= `max_char_spacing`.
- Collapse any consecutive characters >= `max_consecutive` into a single character.
- Convert the name to lowercase if the number of consecutive uppercase >= `max_consecutive_upper`.
- Dehoist the name if `dehoist` is true, removing any leading non-alphanumeric characters.
- Remove parentheses containing single characters and otherwise normalize parentheses.
- Prepend or append the stored leading/trailing emoji characters.
- Trim the name to 32 characters if it still exceeds the limit.
- If the name is empty, use the `fallback_name`.

#### Member Structure

| Field    | Type                |
| -------- | ------------------- |
| id       | snowflake           |
| username | string              |
| nickname | ?string             |
| roles    | array of snowflakes |

#### Sanitize Structure

All fields are optional except members, which must contain at least one member.

| Field                  | Type                                         | Description                                           |
| ---------------------- | -------------------------------------------- | ----------------------------------------------------- |
| members                | array of [member](#member-structure) objects | List of members to sanitize (1-1000)                  |
| dehoist?               | boolean                                      | Strip leading non-alphanum chars (default `true`)     |
| exclude_roles?         | array of snowflakes                          | Role IDs to exclude from sanitization                 |
| exclude_users?         | array of snowflakes                          | User IDs to exclude from sanitization                 |
| fallback_name?         | string                                       | Failed sanitization fallback (default `ZChange Name`) |
| force_username?        | boolean                                      | Force the username to be used (default `false`)       |
| max_char_spacing?      | integer                                      | Max spacing between chars (default unset)             |
| max_consecutive?       | integer                                      | Max consecutive chars (default unset)                 |
| max_consecutive_upper? | integer                                      | Max consecutive uppercase chars (default unset)       |
| max_emoji_leading?     | integer                                      | Max leading emoji chars (default `0`)                 |
| max_emoji_trailing?    | integer                                      | Max trailing emoji chars (default `0`)                |
| max_spaces?            | integer                                      | Max spaces or remove all (default unset)              |
| normalize_parentheses? | boolean                                      | Normalize parentheses (default `true`)                |
| replace_char?          | string                                       | Invalid replacement character (default empty string)  |

#### Example Request Body

```json
{
  "members": [
    {
      "id": "123456789012345678",
      "username": "Username",
      "nickname": "!!!𝓡𝓮𝓮𝓮𝓮𝓮𝓮𝓮𝓮𝓮𝓮 😎",
      "roles": []
    }
  ],
  "max_consecutive": 4
}
```

#### Example Response Body

```json
{
  "123456789012345678": "Reeee"
}
```
