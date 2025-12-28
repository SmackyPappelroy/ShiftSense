from app.services.importers import import_plc_text
from app.analytics.engine import analyze_plc_code
from app.models.models import Workspace
from app.db.session import SessionLocal


def test_plc_analysis_findings():
    db = SessionLocal()
    workspace = Workspace(name="Demo", customer="ACME")
    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    plc_code = """FOR i := 1 TO 100 DO\narrayData[i] := i;\nEND_FOR;\nCASE state OF\n1: action := TRUE;\nEND_CASE;\n"""
    dataset = import_plc_text(db, workspace.id, "main.st", plc_code, language="st")
    findings = analyze_plc_code(db, dataset)
    assert len(findings) >= 2
    db.close()
