"""add unique constraint on races.name

Revision ID: 1a7c4e9b2d30
Revises: 0549f5dad877
Create Date: 2026-09-09 10:40:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1a7c4e9b2d30"
down_revision: str | Sequence[str] | None = "0549f5dad877"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # POST /races already rejected duplicates in Python; this closes the
    # race condition and the seed-run-twice case at the database level.
    op.create_unique_constraint("uq_races_name", "races", ["name"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_races_name", "races", type_="unique")
