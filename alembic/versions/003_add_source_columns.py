"""003_add_source_columns

Revision ID: 003
Revises: 002
Create Date: 2026-06-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add nullable columns
    op.add_column("trending_posts", sa.Column("source", sa.String(20), nullable=True))
    op.add_column("trending_posts", sa.Column("source_id", sa.String(100), nullable=True))

    # 2. Backfill from hn_id
    op.execute(
        "UPDATE trending_posts SET source = 'hackernews', source_id = hn_id"
    )

    # 3. Make NOT NULL
    op.alter_column("trending_posts", "source", nullable=False)
    op.alter_column("trending_posts", "source_id", nullable=False)

    # 4. Drop old unique constraint
    op.drop_constraint("trending_posts_hn_id_key", "trending_posts", type_="unique")

    # 5. Add new unique constraint
    op.create_unique_constraint(
        "uq_trending_source_source_id", "trending_posts", ["source", "source_id"]
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_trending_source_source_id", "trending_posts", type_="unique"
    )
    op.create_unique_constraint(
        "trending_posts_hn_id_key", "trending_posts", ["hn_id"]
    )
    op.drop_column("trending_posts", "source_id")
    op.drop_column("trending_posts", "source")
