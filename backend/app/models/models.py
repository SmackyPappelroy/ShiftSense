from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base


class Workspace(Base):
    __tablename__ = "workspaces"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    customer = Column(String, nullable=False)
    site = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    datasets = relationship("DatasetVersion", back_populates="workspace")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="Engineer")
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, nullable=False)
    target = Column(String, nullable=False)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class DatasetVersion(Base):
    __tablename__ = "dataset_versions"
    id = Column(Integer, primary_key=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    source = Column(String, nullable=False)
    checksum = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="datasets")
    tags = relationship("Tag", back_populates="dataset")
    findings = relationship("Finding", back_populates="dataset")


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("dataset_versions.id"))
    name = Column(String, nullable=False)
    unit = Column(String, nullable=True)
    type = Column(String, nullable=True)
    source = Column(String, nullable=True)
    area = Column(String, nullable=True)

    dataset = relationship("DatasetVersion", back_populates="tags")
    events = relationship("Event", back_populates="tag")

    __table_args__ = (UniqueConstraint("dataset_id", "name", name="uq_tag_dataset_name"),)


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"))
    ts = Column(DateTime, nullable=False)
    value = Column(Float, nullable=True)
    quality = Column(String, default="good")

    tag = relationship("Tag", back_populates="events")


class Alarm(Base):
    __tablename__ = "alarms"
    id = Column(Integer, primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"))
    ts_on = Column(DateTime, nullable=False)
    ts_off = Column(DateTime, nullable=True)
    priority = Column(Integer, default=3)
    message = Column(String, nullable=False)


class CodeArtifact(Base):
    __tablename__ = "code_artifacts"
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("dataset_versions.id"))
    file = Column(String, nullable=False)
    language = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    hash = Column(String, nullable=False)


class Finding(Base):
    __tablename__ = "findings"
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("dataset_versions.id"))
    category = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(JSON, nullable=False)
    recommendation = Column(Text, nullable=False)
    expected_gain = Column(String, nullable=True)
    risk = Column(String, nullable=True)
    status = Column(String, default="New")
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("DatasetVersion", back_populates="findings")


class FeatureFlag(Base):
    __tablename__ = "feature_flags"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    enabled = Column(Boolean, default=True)


class ImportJob(Base):
    __tablename__ = "import_jobs"
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("dataset_versions.id"))
    status = Column(String, default="completed")
    details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
