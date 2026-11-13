# Lab 5 - Data model worksheet

## 1. Critique the bad schema (`sql/bad_schema.sql`)

| # | Problem | Why it hurts | Fix and actual implementation boundary |
| --- | --- | --- | --- |
| 1 | `chats.id` has no primary key or uniqueness constraint. | Duplicate or null identifiers make references ambiguous. | Each core table has a primary key; `interaction.request_id` is also unique and not null. |
| 2 | Names, phone numbers, full messages and answers are retained without a stated purpose or expiry. | Copies can expose personal details and increase the impact of a leak. | Omit names, phone numbers and raw chat content; retain a salted session hash and necessary metadata. Retention below is a proposal, not an implemented cleanup job. |
| 3 | `feedback` is a comma-separated text list. | Ratings cannot be validated or joined individually; authors cannot timestamp each rating. | One `feedback` row per rating, with its own ID, numeric rating, timestamp and optional comment. Migration 001 adds a rating CHECK; the ORM relies on API validation. |
| 4 | A single chats table does not represent sessions and feedback relationships explicitly. | Session data is duplicated and feedback cannot reliably reference an answer. | Separate `chat_session`, `interaction` and `feedback`. Link interactions to the session ID and feedback to the unique request ID. Enable/check SQLite FK enforcement separately; declarations alone do not guarantee it. |
| 5 | `time` is ambiguous text and `latency` contains units such as `120ms`. | Sorting dates and computing numeric averages becomes unreliable. | Use UTC timestamps in `created_at` and numeric `latency_ms`. SQLite does not automatically enforce every declared timestamp/type constraint. |
| 6 | `intent` is unconstrained free text with inconsistent spellings. | `fee`, `Fee` and `tuition` split one category into several groups. | The service emits canonical Intent enum values. The supplied DB column is still text without an enum CHECK; direct database writers must follow the same vocabulary. |

## 2. Store or not? (privacy-aware storage)

The following expiry periods are proposed product decisions for team review.
The starter currently has no automatic purge, anonymization or aggregation job.
A salted, truncated session hash is pseudonymous, not proof of anonymity.

| Data | Store? | Form | Proposed retention | Reason |
| --- | --- | --- | --- | --- |
| raw user message | No | none | Never persist | May contain private details; counts and latency do not require the message. |
| session id | Yes, indirectly | SHA-256(salt + raw ID), first 16 hex characters | Remove after all linked interactions expire, at most 90 days after last activity | Counts sessions without persisting the raw identifier. Keep a private stable salt outside Git. |
| intent, latency, topic | Yes | typed metadata; optionally aggregate later | 90 days for individual rows | Supports routing, performance and unresolved-topic analysis. Aggregate retention requires a separate implementation decision. |
| feedback rating | Yes | integer -1, 0 or 1, linked to a request ID | At most 90 days, delete before its parent interaction | Supports quality analysis while preserving referential integrity. |
| feedback comment | Optional | raw bounded text, up to 500 characters at the API | Clear comment text after 30 days; retain allowed rating until its expiry | Comments can contain personal information even though the field is allowed. Use synthetic examples and avoid requesting personal details. |
| student name / phone | No | none | Never persist | No Lab 5 feature requires these identifiers. |

## 3. Product questions to fields

| Product question | Fields needed | Tables | Query sketch |
| --- | --- | --- | --- |
| Most failed intent? | intent, resolved | interaction | `SELECT intent, COUNT(*) AS unresolved FROM interaction WHERE resolved = 0 GROUP BY intent ORDER BY unresolved DESC, intent;` |
| Average response time by intent? | intent, latency_ms | interaction | `SELECT intent, ROUND(AVG(latency_ms), 1) AS avg_latency_ms FROM interaction GROUP BY intent ORDER BY avg_latency_ms DESC, intent;` |
| Top unresolved topics? | topic, resolved | interaction | `SELECT topic, COUNT(*) AS unresolved FROM interaction WHERE resolved = 0 GROUP BY topic ORDER BY unresolved DESC, topic;` |

Here, "failed" means `resolved = 0`, following the team's contract; it does not
mean `degraded = 1` or a negative feedback rating. Those are independent signals.
A null topic means no source/topic was assigned and must be reported as such.
Under the current routing rule, unknown answers commonly have a null topic.

## 4. ER diagram

See [the ER diagram and implementation notes](data-model.md).
