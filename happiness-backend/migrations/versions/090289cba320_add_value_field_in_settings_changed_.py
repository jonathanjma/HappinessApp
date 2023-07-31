"""Add value field in settings, changed bool name

Revision ID: 090289cba320
Revises: 9c7e031ea696
Create Date: 2023-06-21 13:53:47.568780

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '090289cba320'
down_revision = 'e8ca78ad78e7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('setting', schema=None) as batch_op:
        batch_op.add_column(sa.Column('enabled', sa.Boolean(), nullable=False))
        batch_op.alter_column('value',
                              existing_type=sa.BOOLEAN(),
                              type_=sa.String(),
                              nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('setting', schema=None) as batch_op:
        batch_op.alter_column('value',
                              existing_type=sa.String(),
                              type_=sa.BOOLEAN(),
                              nullable=False)
        batch_op.drop_column('enabled')

    # ### end Alembic commands ###
