"""adding previous race to history db

Revision ID: d1b934f658a0
Revises: 40cbd724a46f
Create Date: 2023-07-09 15:03:22.276044

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1b934f658a0'
down_revision = '40cbd724a46f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('quiz_answers_history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('previous_race', sa.String(length=255), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('quiz_answers_history', schema=None) as batch_op:
        batch_op.drop_column('previous_race')

    # ### end Alembic commands ###
