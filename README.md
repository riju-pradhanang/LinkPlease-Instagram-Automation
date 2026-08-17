# LinkPlease — Part A

Instagram comment → DM automation service built on top of a deliberately hostile mock Instagram API (PseudoGram).

## Architecture

```
[ Incoming Webhook ] ──▶ [ Event Storage (Idempotent by event_id) ]
                               │
                               ▼ (FastAPI Background Task)
                     [ Rule Matching & Dedup Gate ] ──▶ UNIQUE (rule_id, recipient_user_id)
                               │                                  │
                               │ (New match)                      │ (Duplicate)
                               ▼                                  ▼
                     [ send_jobs Table ]                 [ stats_counters (duplicates_blocked++) ]
                               ▲
                               │ (Async Worker Loop with Rate Limiter & Exponential Backoff)
                     [ Send Worker ] ──▶ PseudoGram API (`/v1/dm/send`)
                               │
                               ▼
                        [ GET /stats ]
```

The system operates in four decoupled stages:
1. **Event Ingestion**: Incoming webhooks from `/webhook` are stored idempotently into PostgreSQL using an `ON CONFLICT DO NOTHING` constraint on `event_id`, returning HTTP 200 immediately within milliseconds.
2. **Rule Matching & Dedup Gate**: A background task inspects new `comment.created` events against active keyword rules (case-insensitive substring match). When matched, it inserts a dispatch job into `send_jobs` backed by a composite `UNIQUE(rule_id, recipient_user_id)` constraint. If a duplicate match occurs (e.g. same user commenting multiple times matching the same rule), PostgreSQL rejects the insert, triggering an atomic increment on `stats_counters.duplicates_blocked`.
3. **Send Worker**: A persistent asynchronous background worker loop continuously polls pending jobs whose `next_attempt_at <= now()`. It enforces a strict rolling rate limiter (max 10 requests / 60s), attaches an `Idempotency-Key` to outgoing API requests, and executes exponential backoff on retries (handling HTTP 500 internal errors and HTTP 429 rate limit backoff headers).
4. **Stats Reporting**: `/stats` aggregates real-time counts directly from `send_jobs` (filtered by delivery status) and `stats_counters`.

---

## API Contract Summary

### 1. `POST /rules`
Creates a trigger rule that sends a DM when a comment contains the given keyword.

- **Request:**
  ```json
  {
    "keyword": "PRICE",
    "dm_message": "Here is the price list: https://example.com/pricing"
  }
  ```
- **Response (`201 Created`):**
  ```json
  {
    "rule_id": "83c24d13-c9de-4e14-a024-40aa4b358dfc",
    "keyword": "PRICE",
    "dm_message": "Here is the price list: https://example.com/pricing"
  }
  ```

### 2. `POST /webhook`
Receives comment events from the platform. Acknowledges within 5 seconds.

- **Request:**
  ```json
  {
    "event_id": "evt_01J8ZQ4K2N7RXA",
    "event_type": "comment.created",
    "sent_at": "2026-08-10T09:14:22.481Z",
    "data": {
      "comment_id": "cmt_9f2a7c",
      "post_id": "post_44de1b",
      "text": "PRICE please",
      "created_at": "2026-08-10T09:14:21.900Z",
      "from": {
        "user_id": "usr_3b91fe",
        "username": "arjun.shoots"
      }
    }
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "status": "ok"
  }
  ```

### 3. `GET /stats`
Reports live counts of DM deliveries, failures, queues, and blocked duplicates.

- **Response (`200 OK`):**
  ```json
  {
    "sent": 0,
    "failed": 3,
    "queued": 8,
    "duplicates_blocked": 14
  }
  ```

---

## Local Setup & Quickstart

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (or local PostgreSQL 16)
- Git

### 1. Clone the repository
```bash
git clone https://github.com/riju-pradhanang/LinkPlease-Instagram-Automation.git
cd LinkPlease-Instagram-Automation
```

### 2. Configure Environment Variables
Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```
Update `.env` with your database credentials and PseudoGram API key:
```env
DATABASE_URL=postgresql+asyncpg://postgres:devpass@localhost:5432/linkplease
PSEUDOGRAM_API_KEY=your_real_api_key_here
```

### 3. Start PostgreSQL Database
```bash
docker run --name linkplease-db -e POSTGRES_PASSWORD=devpass -e POSTGRES_DB=linkplease -p 5432:5432 -d postgres:16
```

Apply database migrations:
```bash
docker exec -i linkplease-db psql -U postgres -d linkplease < migrations/schema.sql
```

### 4. Setup Python Environment & Dependencies
```bash
python -m venv venv
# On Linux/macOS:
source venv/bin/activate
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 5. Run the Application
```bash
uvicorn app.main:app --reload
```
The server will start at `http://localhost:8000`.

### 6. Run Tests
```bash
pytest
```

---

## Deployment

The application is configured for deployment on Render using the included [`Procfile`](file:///c:/Users/Dell/Desktop/linkpleaseIGAutomation/linkplease/Procfile):
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
Make sure to set `DATABASE_URL` (with `postgresql+asyncpg://` prefix) and `PSEUDOGRAM_API_KEY` in your production environment settings.