"""002_add_trending_posts

Revision ID: 002
Revises: 001
Create Date: 2026-06-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "trending_posts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("hn_id", sa.String(50), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("url", sa.String(1000), nullable=True),
        sa.Column("points", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("comment_count", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("author", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scraped_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("topic_tags", sa.ARRAY(sa.String(100)), nullable=True),
        sa.Column("is_visible", sa.Boolean(), server_default=sa.text("true"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hn_id"),
    )


def downgrade() -> None:
    op.drop_table("trending_posts")
