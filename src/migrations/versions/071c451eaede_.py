"""empty message

Revision ID: 071c451eaede
Revises: 
Create Date: 2025-01-01 11:47:51.008451

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '071c451eaede'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('saves',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('file_id', sa.String(), nullable=False),
    sa.Column('media_type', sa.Enum('VIDEO', 'PHOTO', 'AUDIO', 'FILE', 'ANIMATION', 'STICKER', 'VOICE', 'VIDEO_NOTE', name='media_type'), nullable=True),
    sa.Column('caption', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('file_id'),
    sa.UniqueConstraint('id', 'file_id')
    )
    op.create_table('users',
    sa.Column('user_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('is_moder', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('user_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_table('saves')
    # ### end Alembic commands ###
