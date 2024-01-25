"""rename user.full_name to user.fullname

Revision ID: 71c129cc19d6
Revises: e49f90c6caac
Create Date: 2024-01-24 21:22:57.602650

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71c129cc19d6'
down_revision: Union[str, None] = 'e49f90c6caac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('fullname', sa.String(), nullable=False))
    op.drop_column('users', 'full_name')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('full_name', sa.VARCHAR(length=250), autoincrement=False, nullable=False))
    op.drop_column('users', 'fullname')
    # ### end Alembic commands ###