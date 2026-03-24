# telephony-service

`telephony-service` is a production-oriented FastAPI backend that handles telephony orchestration for taxi calls.

## Responsibilities
- Receive Twilio-style incoming call webhooks
- Manage call sessions and state transitions
- Collect multi-step voice recordings (origin / destination / notes)
- Handle DTMF input (confirm/re-record/cancel)
- Delegate routing and order processing to a core backend

This service intentionally avoids deep business logic.

## Stack
- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- Pydantic v2 + pydantic-settings
- Alembic
- httpx
- pytest

## Local setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment variables
- `DATABASE_URL` (default: `sqlite:///./telephony.db`)
- `CORE_BACKEND_BASE_URL` (default: `http://localhost:8001`)
- `CORE_BACKEND_TIMEOUT_SECONDS` (default: `10`)
- `LOG_LEVEL` (default: `INFO`)
- `DEFAULT_CALLER_ID` (optional)

## Run app
```bash
uvicorn app.main:app --reload
```

## Migrations
```bash
alembic upgrade head
```

## Example webhook calls
Incoming call:
```bash
curl -X POST http://localhost:8000/webhooks/voice/incoming \
  -d "CallSid=CA123" \
  -d "From=+972541234567" \
  -d "To=+972500000000"
```

Origin recording:
```bash
curl -X POST http://localhost:8000/webhooks/voice/recordings/origin \
  -d "CallSid=CA123" \
  -d "RecordingSid=RECAAA" \
  -d "RecordingUrl=https://example.com/rec-origin" \
  -d "RecordingDuration=4"
```

DTMF confirm:
```bash
curl -X POST http://localhost:8000/webhooks/voice/dtmf/confirm \
  -d "CallSid=CA123" \
  -d "Digits=1"
```

## Tests
```bash
pytest -q
```
