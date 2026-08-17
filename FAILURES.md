# Failures and Edge Cases Log

This document tracks known failure modes, race conditions, edge cases, and post-mortem analysis for the linkplease IG Automation service.

## 1. Concurrent Webhook Event Deduplication
- **Risk**: Concurrent calls with the same webhook payload / event ID could bypass application-level check and cause duplicate send jobs.
- **Mitigation**: Database unique constraint on `(event_id, platform)` or `idempotency_key`. SQLite / PostgreSQL atomic handling.

## 2. Sender Job Failures & Retries
- **Risk**: Mock API or target endpoint timing out or returning 5xx errors.
- **Mitigation**: Exponential backoff retry loop with status tracking (`PENDING`, `PROCESSING`, `SUCCESS`, `FAILED`).

## 3. Webhook Burst Traffic
- **Risk**: High frequency webhooks blocking API handlers.
- **Mitigation**: Asynchronous ingestion pipeline; immediate DB record creation and response, background worker execution for sending.
