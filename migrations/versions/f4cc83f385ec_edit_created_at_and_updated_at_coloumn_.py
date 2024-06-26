"""edit created_at and updated_at coloumn names

Revision ID: f4cc83f385ec
Revises: 84e725c99dbe
Create Date: 2024-01-24 15:59:01.907123

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f4cc83f385ec'
down_revision: Union[str, None] = '84e725c99dbe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
        op.add_column('medias', sa.Column('created_at', sa.DateTime(), nullable=True))
        op.add_column('medias', sa.Column('updated_at', sa.DateTime(), nullable=True))
        op.drop_column('medias', 'updated_on')
        op.drop_column('medias', 'created_on')
        op.add_column('pokaks', sa.Column('created_at', sa.DateTime(), nullable=True))
        op.drop_column('pokaks', 'created_on')
        op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))
        op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))
        op.drop_column('users', 'updated_on')
        op.drop_column('users', 'created_on')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
        op.add_column('users', sa.Column('created_on', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        op.add_column('users', sa.Column('updated_on', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        op.drop_column('users', 'updated_at')
        op.drop_column('users', 'created_at')
        op.add_column('pokaks', sa.Column('created_on', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        op.drop_column('pokaks', 'created_at')
        op.add_column('medias', sa.Column('created_on', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        op.add_column('medias', sa.Column('updated_on', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        op.drop_column('medias', 'updated_at')
        op.drop_column('medias', 'created_at')
    # ### end Alembic commands ###
