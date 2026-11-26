# External mock service

Independent black-box mock service on port 8081. It provides `GET /health`, `GET /api/v1/exercises?muscleGroup=...`, and `POST /api/v1/calendar/events`. Business requests require `X-API-Key`; configure the same local development key through `EXTERNAL_API_KEY` for both services. The mock returns example exercise data and a generated `externalEventId`; it does not persist calendar events.
