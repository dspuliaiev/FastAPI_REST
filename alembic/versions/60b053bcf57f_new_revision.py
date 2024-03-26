"""New revision

Revision ID: 60b053bcf57f
Revises: 
Create Date: 2024-03-26 11:44:56.160533

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '60b053bcf57f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'contacts',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('first_name', sa.String),
        sa.Column('last_name', sa.String),
        sa.Column('email', sa.String, unique=True),
        sa.Column('phone_number', sa.String, unique=True),
        sa.Column('birthday', sa.Date),
        sa.Column('additional_data', sa.String, nullable=True)
    )

def downgrade() -> None:
    op.drop_table('contacts')
