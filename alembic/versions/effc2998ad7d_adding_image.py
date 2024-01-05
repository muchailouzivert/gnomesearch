"""adding image

Revision ID: effc2998ad7d
Revises: 
Create Date: 2023-12-13 15:21:30.594751

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'effc2998ad7d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "films",
        sa.Column('image', sa.String(200))

    )


def downgrade() -> None:
    pass
