"""add encrypted key recovery

Revision ID: 1337704656c3
Revises: 090289cba320
Create Date: 2023-07-19 22:25:07.037928

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1337704656c3'
down_revision = '090289cba320'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('encrypted_key_recovery', sa.LargeBinary(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('encrypted_key_recovery')

    # ### end Alembic commands ###
