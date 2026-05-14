# Mention Rules

Use native mention fields when the user wants someone in a KIM group to receive a real reminder.

## Hard Rules

- Native mentions are for group messages only.
- Put exact KIM usernames in `mentionUsernames`.
- Prefer plain usernames such as `alice`.
- Do not use display names such as `Alice Zhang` in `mentionUsernames`.
- Keep `message` as plain text when using native mentions.
- Remove duplicate fake `@alice` text from the body if `mentionUsernames` is already set.
- Use `mentionAll: true` for native `@all`.
- Do not put both fake `@all` text and `mentionAll: true` in the same message body.

## Preferred Shapes

Group message that should truly notify one user:

```json
{
  "channel": "kim",
  "target": "space:987654",
  "message": "吃饭了吗？",
  "mentionUsernames": ["alice"]
}
```

Group message that should notify multiple users:

```json
{
  "channel": "kim",
  "target": "space:987654",
  "message": "请两位确认一下今晚值班安排。",
  "mentionUsernames": ["alice", "bob"]
}
```

Group message that should notify everyone:

```json
{
  "channel": "kim",
  "target": "space:987654",
  "message": "请大家五分钟内查看公告。",
  "mentionAll": true
}
```

## Anti-Patterns

Do not do this:

```json
{
  "channel": "kim",
  "target": "space:987654",
  "message": "@alice 吃饭了吗？",
  "mentionUsernames": ["alice"]
}
```

Reason: the bare `@alice` text is fake and duplicates the real native mention.
