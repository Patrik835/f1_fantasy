"""added q11

Revision ID: 2ce2d137c182
Revises: ea18a33f2e9a
Create Date: 2023-05-22 15:45:44.844746

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ce2d137c182'
down_revision = 'ea18a33f2e9a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('quiz_answers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('q11', sa.String(length=255), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('quiz_answers', schema=None) as batch_op:
        batch_op.drop_column('q11')

    # ### end Alembic commands ###
