CREATE TABLE rules (
    rule_id     TEXT PRIMARY KEY,
    keyword     TEXT NOT NULL,
    dm_message  TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE events (
    event_id    TEXT PRIMARY KEY,     -- dedup at ingestion happens here
    event_type  TEXT NOT NULL,
    comment_id  TEXT,
    post_id     TEXT,
    comment_text TEXT,
    from_user_id TEXT,
    from_username TEXT,
    sent_at     TIMESTAMPTZ,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    raw_payload JSONB NOT NULL
);

CREATE TABLE send_jobs (
    id                  BIGSERIAL PRIMARY KEY,
    rule_id             TEXT NOT NULL REFERENCES rules(rule_id),
    recipient_user_id   TEXT NOT NULL,
    comment_id          TEXT,
    dm_message          TEXT NOT NULL,
    status              TEXT NOT NULL DEFAULT 'pending',
        -- pending | sending | queued | delivered | failed
    dm_id               TEXT,
    attempts            INT NOT NULL DEFAULT 0,
    next_attempt_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (rule_id, recipient_user_id)   -- THE constraint. Everything hinges on this line.
);

CREATE TABLE stats_counters (
    duplicates_blocked  BIGINT NOT NULL DEFAULT 0
);
INSERT INTO stats_counters (duplicates_blocked) VALUES (0);