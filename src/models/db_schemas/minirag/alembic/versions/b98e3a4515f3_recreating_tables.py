"""recreating tables

Revision ID: b98e3a4515f3
Revises: cc8e0f625b86
Create Date: 2026-04-28 03:06:09.206664

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b98e3a4515f3'
down_revision: Union[str, Sequence[str], None] = 'cc8e0f625b86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Earlier revisions already create the relational tables.
    # Keep only the cleanup of the old pgvector collection table if it exists.
    op.execute("DROP TABLE IF EXISTS project_1024_12")


def downgrade() -> None:
    """Downgrade schema."""
    pass
