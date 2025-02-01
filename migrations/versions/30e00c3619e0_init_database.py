"""init database

Revision ID: 30e00c3619e0
Revises: 
Create Date: 2025-02-01 17:54:59.565135

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30e00c3619e0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shopping_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shopping_items_category'), 'shopping_items', ['category'], unique=False)
    op.create_index(op.f('ix_shopping_items_id'), 'shopping_items', ['id'], unique=False)
    op.create_index(op.f('ix_shopping_items_name'), 'shopping_items', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_shopping_items_name'), table_name='shopping_items')
    op.drop_index(op.f('ix_shopping_items_id'), table_name='shopping_items')
    op.drop_index(op.f('ix_shopping_items_category'), table_name='shopping_items')
    op.drop_table('shopping_items')
    # ### end Alembic commands ###
