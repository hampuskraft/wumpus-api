# Wumpus API

Discord member username & nickname sanitization API. A hosted version is available at https://api.wump.io/v1.

## API Endpoints

### `POST /sanitize`

Produces a key-value map of member IDs → sanitized names.

#### Sanitization Rules

Sanitization is performed in the following order:

1. If the member has any roles specified in `exclude_roles`, skip sanitization.
2. If the member ID is in `exclude_users`, skip sanitization.
3. Use the member's nickname if set, else the username. (Override with the `force_username` option.)
4. Run [Unidecode](https://pypi.org/project/Unidecode/) on the name to convert Unicode characters to ASCII equivalents.
5. If a character has no ASCII equivalent, replace it with the character specified in `replace_char`.
6. Collapse any consecutive characters >= `max_consecutive` into a single character.
7. Convert the name to lowercase if the number of consecutive uppercase >= `max_consecutive_upper`.
8. Dehoist the name if `dehoist` is true, removing any leading non-alphanumeric characters.
9. Strip any leading, trailing, or consecutive whitespace from the name and trim it to 32 characters.
10. If the name is empty, use the fallback name.

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
| max_consecutive?       | integer                                      | Max consecutive chars (default unset)                 |
| max_consecutive_upper? | integer                                      | Max consecutive uppercase chars (default unset)       |
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
