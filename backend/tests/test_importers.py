from app.services.importers import import_csv_timeseries
from app.analytics.engine import analyze_timeseries
from app.models.models import Workspace
from app.db.session import SessionLocal


def test_csv_import_and_analysis():
    db = SessionLocal()
    workspace = Workspace(name="Demo", customer="ACME")
    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    csv_content = "ts,tag,value\n2024-01-01T00:00:00,cycle_signal,1\n2024-01-01T00:00:10,cycle_signal,0\n2024-01-01T00:00:20,energy_kwh,12\n2024-01-01T00:00:30,alarm_status,1\n"
    dataset, _ = import_csv_timeseries(db, workspace.id, csv_content)
    findings = analyze_timeseries(db, dataset)
    assert len(findings) >= 3
    db.close()
