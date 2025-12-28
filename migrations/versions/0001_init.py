"""init

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "workspaces",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("customer", sa.String(), nullable=False),
        sa.Column("site", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("target", sa.String(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "dataset_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("workspace_id", sa.Integer(), sa.ForeignKey("workspaces.id")),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("checksum", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dataset_id", sa.Integer(), sa.ForeignKey("dataset_versions.id")),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("unit", sa.String(), nullable=True),
        sa.Column("type", sa.String(), nullable=True),
        sa.Column("source", sa.String(), nullable=True),
        sa.Column("area", sa.String(), nullable=True),
    )
    op.create_unique_constraint("uq_tag_dataset_name", "tags", ["dataset_id", "name"])
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tag_id", sa.Integer(), sa.ForeignKey("tags.id")),
        sa.Column("ts", sa.DateTime(), nullable=False),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("quality", sa.String(), nullable=True),
    )
    op.create_table(
        "alarms",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tag_id", sa.Integer(), sa.ForeignKey("tags.id")),
        sa.Column("ts_on", sa.DateTime(), nullable=False),
        sa.Column("ts_off", sa.DateTime(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=True),
        sa.Column("message", sa.String(), nullable=False),
    )
    op.create_table(
        "code_artifacts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dataset_id", sa.Integer(), sa.ForeignKey("dataset_versions.id")),
        sa.Column("file", sa.String(), nullable=False),
        sa.Column("language", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("hash", sa.String(), nullable=False),
    )
    op.create_table(
        "findings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dataset_id", sa.Integer(), sa.ForeignKey("dataset_versions.id")),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("expected_gain", sa.String(), nullable=True),
        sa.Column("risk", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "feature_flags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=True),
    )
    op.create_index("ix_feature_flags_name", "feature_flags", ["name"], unique=True)
    op.create_table(
        "import_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dataset_id", sa.Integer(), sa.ForeignKey("dataset_versions.id")),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table("import_jobs")
    op.drop_index("ix_feature_flags_name", table_name="feature_flags")
    op.drop_table("feature_flags")
    op.drop_table("findings")
    op.drop_table("code_artifacts")
    op.drop_table("alarms")
    op.drop_table("events")
    op.drop_constraint("uq_tag_dataset_name", "tags", type_="unique")
    op.drop_table("tags")
    op.drop_table("dataset_versions")
    op.drop_table("audit_logs")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_table("workspaces")
