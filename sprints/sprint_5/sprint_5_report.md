# Sprint 5 Report — Eval + Demo Hardening

## Summary

The demo is runnable through Docker Compose at `http://localhost:3001` in this environment. Backend, retrieval, SSE chat, frontend build, and eval smoke tests pass against the bundled mock corpus.

## Validation

| Check | Result |
|---|---|
| Backend tests | Passed (`pytest backend/tests`) |
| Eval harness | Passed 6/6 (`scripts/eval_run.py`) |
| Frontend build | Passed (`npm run build`) |
| Docker Compose build | Passed |
| Frontend HTTP smoke | Passed (`http://localhost:3001`) |
| SSE chat smoke | Passed |

## Five Dry Runs

| Run | Scenario | Result | Latency |
|---|---|---|---|
| 1 | Hugin planning Q1 | Final answer + citations | 0.599s |
| 2 | Design vs execution Q2 | Final answer + citations | 0.255s |
| 3 | F-11 vs F-14 comparison | Final answer + citations | 0.336s |
| 4 | Stuck pipe events | Final answer + citations | 0.469s |
| 5 | Production-rate off-script question | Final answer + citations | 0.381s |

## Notes

- Real Volve PDFs are not yet exported; the app runs against a curated mock corpus with the same chunk/document shape.
- Backend host port is not published by default to avoid conflicts; Next.js proxies to the backend inside Docker Compose.
- Frontend host port defaults to `3001` because `3000` was occupied on this machine.
- External SME review remains a pre-customer gate.
