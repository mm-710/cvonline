# Target Rules

Resolve the message destination before thinking about mentions.

## Destination Mapping

| Scenario | Preferred target | Notes |
| --- | --- | --- |
| Send a direct message to a known KIM username | `username:alice` | Preferred for stability |
| Send a direct message when an explicit KIM user id is provided | `user:123456` | Use only if the id is explicitly known |
| Send a message to a KIM group | `space:987654` | Group sends must use `space:` |

## Hard Rules

- Do not use a group id in a user target.
- Do not use a username as a group target.
- Do not confuse the destination with the people to mention.
- A direct message target and a group mention target are different things.
- Even though bare usernames may work in some flows, prefer explicit `username:` targets in this skill.

## Examples

Direct message to a user:

```json
{
  "channel": "kim",
  "target": "username:alice",
  "message": "你好，麻烦看下这个问题。"
}
```

Message to a group:

```json
{
  "channel": "kim",
  "target": "space:987654",
  "message": "大家下午两点开会。"
}
```
