from collections import defaultdict
from statistics import mean, quantiles
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import Event, Tag, Finding, DatasetVersion, CodeArtifact


def _build_evidence(samples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return samples[:5]


def analyze_timeseries(db: Session, dataset: DatasetVersion) -> List[Finding]:
    tags = db.query(Tag).filter(Tag.dataset_id == dataset.id).all()
    events = db.query(Event).join(Tag).filter(Tag.dataset_id == dataset.id).all()

    findings: List[Finding] = []
    tag_events: Dict[int, List[Event]] = defaultdict(list)
    for event in events:
        tag_events[event.tag_id].append(event)

    cycle_durations = []
    for tag in tags:
        if "cycle" in tag.name.lower():
            values = sorted(tag_events[tag.id], key=lambda e: e.ts)
            start = None
            for event in values:
                if event.value and event.value > 0.9 and start is None:
                    start = event.ts
                elif event.value and event.value < 0.1 and start:
                    cycle_durations.append((event.ts - start).total_seconds())
                    start = None

    if cycle_durations:
        p95 = quantiles(cycle_durations, n=20)[-1]
        average = mean(cycle_durations)
        evidence = _build_evidence(
            [{"type": "timeseries", "metric": "cycle_duration", "value": d} for d in cycle_durations[:5]]
        )
        findings.append(
            Finding(
                dataset_id=dataset.id,
                category="performance",
                severity="medium",
                confidence=0.72,
                title="Cykeltider varierar mer än normalt",
                description=f"Cykeltidsanalys visar P95 {p95:.2f}s och snitt {average:.2f}s.",
                evidence=evidence,
                recommendation="Identifiera steg med hög variation och inför väntelogik eller sekvensoptimering.",
                expected_gain="Stabilare cykeltider och högre throughput.",
                risk="Låg risk vid verifiering i testmiljö.",
            )
        )

    energy_tags = [t for t in tags if "kwh" in t.name.lower() or "energy" in t.name.lower()]
    if energy_tags:
        tag = energy_tags[0]
        values = [e.value for e in tag_events[tag.id] if e.value is not None]
        if values:
            baseline = mean(values)
            evidence = _build_evidence(
                [{"type": "timeseries", "tag": tag.name, "value": v} for v in values[:5]]
            )
            findings.append(
                Finding(
                    dataset_id=dataset.id,
                    category="energy",
                    severity="high",
                    confidence=0.68,
                    title="Hög baslast för energiförbrukning",
                    description=f"Genomsnittlig energinivå {baseline:.2f} indikerar potential för standby-logik.",
                    evidence=evidence,
                    recommendation="Inför standby-läge eller sekvensstyrning för att minska baslast under idle.",
                    expected_gain="Minskad energiförbrukning per cykel.",
                    risk="Kräver verifiering av säker drift vid standby.",
                )
            )

    alarm_like = [t for t in tags if "alarm" in t.name.lower()]
    if alarm_like:
        tag = alarm_like[0]
        values = [e for e in tag_events[tag.id] if e.value is not None]
        evidence = _build_evidence(
            [{"type": "timeseries", "tag": tag.name, "value": e.value, "ts": e.ts.isoformat()} for e in values[:5]]
        )
        findings.append(
            Finding(
                dataset_id=dataset.id,
                category="alarms",
                severity="medium",
                confidence=0.64,
                title="Indikation på chattering i alarmtagg",
                description="Snabba växlingar i larmindikator tyder på chattering och kan skapa larmfloods.",
                evidence=evidence,
                recommendation="Inför debounce/deadband samt se över prioritet och larmtext.",
                expected_gain="Färre onödiga larm och bättre larmkvalitet.",
                risk="Låg risk vid införande av deadband.",
            )
        )

    if len(findings) < 3:
        samples = []
        for tag in tags[:1]:
            samples = _build_evidence(
                [{"type": "timeseries", "tag": tag.name, "note": "Data coverage"}]
            )
        findings.append(
            Finding(
                dataset_id=dataset.id,
                category="maintenance",
                severity="low",
                confidence=0.55,
                title="Begränsad data för prediktivt underhåll",
                description="Data coverage är begränsad vilket gör att prediktiva analyser har låg säkerhet.",
                evidence=samples,
                recommendation="Komplettera med driftloggar och fler sensorer för stabil baseline.",
                expected_gain="Förbättrad diagnostik vid framtida analyser.",
                risk="Ingen direkt risk, datainsamling behövs.",
            )
        )

    db.add_all(findings)
    db.commit()
    return findings


def analyze_plc_code(db: Session, dataset: DatasetVersion) -> List[Finding]:
    artifacts = db.query(CodeArtifact).filter(CodeArtifact.dataset_id == dataset.id).all()
    findings: List[Finding] = []
    for artifact in artifacts:
        lines = artifact.content.splitlines()
        for idx, line in enumerate(lines, start=1):
            if "FOR" in line.upper() and "TO" in line.upper():
                findings.append(
                    Finding(
                        dataset_id=dataset.id,
                        category="performance",
                        severity="high",
                        confidence=0.74,
                        title="Tung loop kan påverka scan-time",
                        description="FOR-loop utan synlig begränsning riskerar ökad scan-time.",
                        evidence=[
                            {
                                "type": "code",
                                "file": artifact.file,
                                "line": idx,
                                "snippet": line.strip(),
                            }
                        ],
                        recommendation="Begränsa loopens iterationer eller flytta tung logik till bakgrund.",
                        expected_gain="Lägre scan-time och stabil drift.",
                        risk="Medel risk - kräver test innan produktionssättning.",
                    )
                )
            if "ARRAY" in line.upper() and "[" in line:
                findings.append(
                    Finding(
                        dataset_id=dataset.id,
                        category="robustness",
                        severity="medium",
                        confidence=0.66,
                        title="Stor array i cyklisk logik",
                        description="Array-iterationer kan ge onödig belastning vid varje cykel.",
                        evidence=[
                            {
                                "type": "code",
                                "file": artifact.file,
                                "line": idx,
                                "snippet": line.strip(),
                            }
                        ],
                        recommendation="Överväg att batcha uppdateringar eller använda eventbaserade triggers.",
                        expected_gain="Jämnare cykeltider och minskad CPU-belastning.",
                        risk="Låg risk vid stegvis förändring.",
                    )
                )
            if "CASE" in line.upper() and "STATE" in line.upper():
                findings.append(
                    Finding(
                        dataset_id=dataset.id,
                        category="robustness",
                        severity="low",
                        confidence=0.61,
                        title="State-maskin bör ha default-hantering",
                        description="Saknar explicit default/else kan ge odefinierade states.",
                        evidence=[
                            {
                                "type": "code",
                                "file": artifact.file,
                                "line": idx,
                                "snippet": line.strip(),
                            }
                        ],
                        recommendation="Lägg till default/else för att hantera okända states.",
                        expected_gain="Ökad robusthet och enklare felsökning.",
                        risk="Låg risk.",
                    )
                )

    if len(findings) < 2 and artifacts:
        line = artifacts[0].content.splitlines()[0] if artifacts[0].content else ""
        findings.append(
            Finding(
                dataset_id=dataset.id,
                category="robustness",
                severity="low",
                confidence=0.52,
                title="Begränsad kodvolym för analys",
                description="Den importerade koden är kort och ger begränsad riskanalys.",
                evidence=[{"type": "code", "file": artifacts[0].file, "line": 1, "snippet": line.strip()}],
                recommendation="Importera fler moduler för djupare analys.",
                expected_gain="Mer heltäckande rekommendationer.",
                risk="Ingen direkt risk.",
            )
        )

    db.add_all(findings)
    db.commit()
    return findings
