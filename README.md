# Wumpus API

Discord member username & nickname sanitization API. A hosted version is available at https://api.wump.io/v1.

> Used in production at [NetherGames Network](https://discord.gg/ng) with over 31,000 members.

## API Endpoints

### `POST /sanitize`

Produces a key-value map of member IDs → sanitized names.

#### Sanitization Rules

Refer to the `sanitize_member` method in [`wumpus/sanitizer.py`](https://github.com/hampuskraft/wumpus-api/blob/main/wumpus/sanitizer.py) for the full list of sanitization rules.

#### Member Structure

| Field           | Type                |
| --------------- | ------------------- |
| id              | snowflake           |
| username        | string              |
| nickname        | ?string             |
| roles           | array of snowflakes |
| force_username? | boolean             |

#### Sanitize Structure

All fields are optional except members, which must contain at least one member.

| Field                  | Type                                         | Description                                           |
| ---------------------- | -------------------------------------------- | ----------------------------------------------------- |
| strict?                | boolean                                      | Strict\* sanitization (default `false`)               |
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
| normalize_brackets?    | boolean                                      | Normalize brackets (default `true`)                   |
| normalize_regional?    | boolean                                      | Normalize regional indicators (default `true`)        |
| replace_char?          | string                                       | Invalid replacement character (default empty string)  |
| strip_pipes_leading?   | boolean                                      | Strip leading `\|` characters (default `true`)        |
| strip_pipes_trailing?  | boolean                                      | Strip trailing `\|` characters (default `true`)       |
| trailing_trademark?    | boolean                                      | Preserve trailing `®` or `™` (default `true`)         |

\* Strict sanitization only allows alphanumeric characters, spaces, underscores, hyphens, and periods. Leading or trailing special characters are stripped. Other normalization and sanitization rules are still applied.

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
