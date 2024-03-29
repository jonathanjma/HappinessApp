"""add reads support

Revision ID: f10cda871fc9
Revises: 1337704656c3
Create Date: 2023-09-10 22:11:49.317672

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f10cda871fc9'
down_revision = '1337704656c3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('readers_happiness',
        sa.Column('happiness_id', sa.Integer(), nullable=True),
        sa.Column('reader_id', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['happiness_id'], ['happiness.id'], ),
        sa.ForeignKeyConstraint(['reader_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('readers_happiness')
    # ### end Alembic commands ###
