"""001_create_tables

Revision ID: 001
Revises:
Create Date: 2026-06-01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "experiences",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("role", sa.String(255), nullable=False),
        sa.Column("period", sa.String(100), nullable=False),
        sa.Column("type", sa.String(100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("highlights", sa.ARRAY(sa.Text()), nullable=True),
        sa.Column("tags", sa.ARRAY(sa.String(100)), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "education",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("school", sa.String(255), nullable=False),
        sa.Column("degree", sa.String(255), nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("period", sa.String(100), nullable=True),
        sa.Column("gpa", sa.String(50), nullable=True),
        sa.Column("details", sa.ARRAY(sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "certifications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("issuer", sa.String(255), nullable=True),
        sa.Column("date", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("language", sa.String(100), nullable=True),
        sa.Column("tags", sa.ARRAY(sa.String(100)), nullable=True),
        sa.Column("github_url", sa.String(500), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("projects")
    op.drop_table("certifications")
    op.drop_table("education")
    op.drop_table("experiences")
