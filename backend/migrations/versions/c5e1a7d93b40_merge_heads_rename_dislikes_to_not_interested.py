"""merge heads and rename dislikes to not_interested

Joins 2078f61f3f1b (update video model) and a1b28ba85806 (create dislikes table),
which both branched from 4ca47b0ede07, and renames the table instead of
recreating it so databases that already applied a1b28ba85806 keep their rows.

Revision ID: c5e1a7d93b40
Revises: 2078f61f3f1b, a1b28ba85806
Create Date: 2026-11-16 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c5e1a7d93b40'
down_revision: Union[str, Sequence[str], None] = ('2078f61f3f1b', 'a1b28ba85806')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (old name, new name); renaming a table in PostgreSQL keeps the old constraint names
CONSTRAINTS = [
    ('dislikes_pkey', 'not_interested_pkey'),
    ('dislikes_user_id_fkey', 'not_interested_user_id_fkey'),
    ('dislikes_video_id_fkey', 'not_interested_video_id_fkey'),
    ('uq_dislikes_user_video', 'uq_not_interested_user_video'),
]


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table('dislikes', 'not_interested')
    for old, new in CONSTRAINTS:
        op.execute(f'ALTER TABLE not_interested RENAME CONSTRAINT {old} TO {new}')


def downgrade() -> None:
    """Downgrade schema."""
    for old, new in CONSTRAINTS:
        op.execute(f'ALTER TABLE not_interested RENAME CONSTRAINT {new} TO {old}')
    op.rename_table('not_interested', 'dislikes')
