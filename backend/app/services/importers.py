import csv
import hashlib
from datetime import datetime
from io import StringIO
from typing import List, Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.models.models import DatasetVersion, Tag, Event, CodeArtifact


def checksum_content(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def import_csv_timeseries(db: Session, workspace_id: int, content: str) -> Tuple[DatasetVersion, List[Event]]:
    dataset = DatasetVersion(
        workspace_id=workspace_id,
        source="csv",
        checksum=checksum_content(content),
    )
    db.add(dataset)
    db.flush()

    reader = csv.DictReader(StringIO(content))
    events: List[Event] = []
    tags_cache = {}
    for row in reader:
        tag_name = row.get("tag") or row.get("Tag") or "unknown"
        if tag_name not in tags_cache:
            tag = Tag(dataset_id=dataset.id, name=tag_name, unit=row.get("unit"))
            db.add(tag)
            db.flush()
            tags_cache[tag_name] = tag
        ts_raw = row.get("ts") or row.get("timestamp") or row.get("time")
        try:
            ts = datetime.fromisoformat(ts_raw)
        except Exception:
            ts = datetime.utcnow()
        value_raw = row.get("value")
        value = float(value_raw) if value_raw not in (None, "") else None
        event = Event(tag_id=tags_cache[tag_name].id, ts=ts, value=value)
        events.append(event)
    db.add_all(events)
    db.commit()
    db.refresh(dataset)
    return dataset, events


def import_plc_text(db: Session, workspace_id: int, filename: str, content: str, language: str) -> DatasetVersion:
    dataset = DatasetVersion(
        workspace_id=workspace_id,
        source="plc_text",
        checksum=checksum_content(content),
    )
    db.add(dataset)
    db.flush()
    artifact = CodeArtifact(
        dataset_id=dataset.id,
        file=filename,
        language=language,
        content=content,
        hash=checksum_content(content),
    )
    db.add(artifact)
    db.commit()
    db.refresh(dataset)
    return dataset


def import_sql_table(
    db: Session,
    workspace_id: int,
    connection_url: str,
    table: str,
    ts_column: str,
    tag_column: str,
    value_column: str,
) -> Tuple[DatasetVersion, int]:
    engine = create_engine(connection_url)
    query = text(f"SELECT {ts_column} as ts, {tag_column} as tag, {value_column} as value FROM {table}")
    dataset = DatasetVersion(
        workspace_id=workspace_id,
        source="sql",
        checksum=checksum_content(f"{connection_url}:{table}"),
    )
    db.add(dataset)
    db.flush()

    tags_cache = {}
    count = 0
    with engine.connect() as connection:
        for row in connection.execute(query):
            tag_name = str(row.tag)
            if tag_name not in tags_cache:
                tag = Tag(dataset_id=dataset.id, name=tag_name)
                db.add(tag)
                db.flush()
                tags_cache[tag_name] = tag
            event = Event(tag_id=tags_cache[tag_name].id, ts=row.ts, value=float(row.value))
            db.add(event)
            count += 1
    db.commit()
    db.refresh(dataset)
    return dataset, count
