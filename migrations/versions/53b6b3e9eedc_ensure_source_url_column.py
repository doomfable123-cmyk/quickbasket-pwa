"""ensure_source_url_column

Revision ID: 53b6b3e9eedc
Revises: 5f9b7831c805
Create Date: 2025-09-16 14:30:59.880358

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53b6b3e9eedc'
down_revision: Union[str, Sequence[str], None] = '5f9b7831c805'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if source_url column exists, if not add it
    try:
        # Try to add the column, will fail silently if it already exists
        with op.batch_alter_table('recipes') as batch_op:
            batch_op.add_column(sa.Column('source_url', sa.String(500), nullable=True))
    except Exception:
        # Column already exists, ignore the error
        pass


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the source_url column
    with op.batch_alter_table('recipes') as batch_op:
        batch_op.drop_column('source_url')
