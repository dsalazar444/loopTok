"""merge heads and rename dislikes to not_interested

Revision ID: 7c3d9e5a1b24
Revises: 2078f61f3f1b, a1b28ba85806
Create Date: 2026-11-15 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '7c3d9e5a1b24'
down_revision: Union[str, Sequence[str], None] = ('2078f61f3f1b', 'a1b28ba85806')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# PostgreSQL keeps the old names after a table rename, so constraints are renamed too.
CONSTRAINTS = [
    ('uq_dislikes_user_video', 'uq_not_interested_user_video'),
    ('dislikes_pkey', 'not_interested_pkey'),
    ('dislikes_user_id_fkey', 'not_interested_user_id_fkey'),
    ('dislikes_video_id_fkey', 'not_interested_video_id_fkey'),
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
