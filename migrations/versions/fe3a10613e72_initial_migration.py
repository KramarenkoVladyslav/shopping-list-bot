"""Initial migration

Revision ID: fe3a10613e72
Revises: 
Create Date: 2025-02-08 16:27:57.249089

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe3a10613e72'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rooms',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('invite_code', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rooms_id'), 'rooms', ['id'], unique=False)
    op.create_index(op.f('ix_rooms_invite_code'), 'rooms', ['invite_code'], unique=True)
    op.create_index(op.f('ix_rooms_name'), 'rooms', ['name'], unique=False)
    op.create_table('room_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('room_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('room_id', 'user_id', name='unique_room_user')
    )
    op.create_index(op.f('ix_room_users_id'), 'room_users', ['id'], unique=False)
    op.create_table('shopping_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('room_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
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
    op.drop_index(op.f('ix_room_users_id'), table_name='room_users')
    op.drop_table('room_users')
    op.drop_index(op.f('ix_rooms_name'), table_name='rooms')
    op.drop_index(op.f('ix_rooms_invite_code'), table_name='rooms')
    op.drop_index(op.f('ix_rooms_id'), table_name='rooms')
    op.drop_table('rooms')
    # ### end Alembic commands ###
