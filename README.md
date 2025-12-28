# ShiftSense

ShiftSense är en AI-driven automationsassistent för att importera, analysera och förbättra automationsprojekt och driftdata med spårbara rekommendationer.

## Funktioner (v1)
- Import av CSV-tidsserier och PLC-textfiler (SCL/ST/Ladder-export) med evidens.
- Normaliserad datamodell för taggar, events, larm, kod och findings.
- Regelbaserade analyser för cykeltid, energi och larmkvalitet.
- Autentisering (JWT), roller och audit-logg-struktur.
- Multi-tenant via Workspaces.
- Feature flags för Energi, Prediktivt, Larm.
- Grundläggande UI med dashboard och findings-lista.

## Kom igång (lokalt via Docker Compose)
1. Starta stacken:
   ```bash
   docker compose up --build
   ```
2. Kör migreringar:
   ```bash
   docker compose exec backend alembic -c /app/alembic.ini upgrade head
   ```
3. Skapa en användare:
   ```bash
   curl -X POST http://localhost:8000/auth/users \
     -H "Content-Type: application/json" \
     -d '{"email": "demo@shiftsense.se", "password": "demo123", "role": "Admin"}'
   ```
4. Logga in och hämta token:
   ```bash
   curl -X POST http://localhost:8000/auth/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=demo@shiftsense.se&password=demo123"
   ```
5. Skapa workspace:
   ```bash
   curl -X POST http://localhost:8000/workspaces \
     -H "Authorization: Bearer <TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"name": "Demo", "customer": "ACME", "site": "Site A"}'
   ```
6. Importera CSV:
   ```bash
   curl -X POST http://localhost:8000/imports/csv/1 \
     -H "Authorization: Bearer <TOKEN>" \
     -F "file=@data/sample_timeseries.csv"
   ```
7. Importera PLC-text:
   ```bash
   curl -X POST http://localhost:8000/imports/plc/1 \
     -H "Authorization: Bearer <TOKEN>" \
     -F "file=@data/sample_plc.st"
   ```
8. Importera från SQL (read-only):
   ```bash
   curl -X POST "http://localhost:8000/imports/sql/1?connection_url=postgresql+psycopg://user:pass@host:5432/db&table=events&ts_column=ts&tag_column=tag&value_column=value" \
     -H "Authorization: Bearer <TOKEN>"
   ```

Frontend finns på http://localhost:5173

## Exempeldata
- `data/sample_timeseries.csv` - syntetisk tidsserie för cykeltid, energi och larm.
- `data/sample_plc.st` - PLC-text med loopar och states.

## Rapportexport (v1)
Rapporter kan exporteras som JSON via API och vidare förädlas till PDF i nästa iteration. Findings returneras via `/findings/{dataset_id}`.

## Licensmodell (förslag)
- Per site (baspaket)
- Tillägg per modul (Energi, Prediktivt, Larm)
- Per användare för avancerade roller

## Roadmap v2
- Fullständig rapportexport (PDF/HTML).
- Tidsserie-indexering i TimescaleDB.
- Bakgrundsjobb/queue för stora importer.
- AI-lager med OpenAI/Azure/local modeller och guardrails.
- Utökad larmanalys med chattering och flood detection.
- Rule Pack Marketplace och kundspecifika paket.
