"""adding QuizAnswersHistory table

Revision ID: 9667f964713c
Revises: ba8d8d6ee708
Create Date: 2023-07-03 14:53:24.814638

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9667f964713c'
down_revision = 'ba8d8d6ee708'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('quiz_answers_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('race_nr', sa.Integer(), nullable=False),
    sa.Column('race_name', sa.String(length=255), nullable=False),
    sa.Column('q1', sa.String(length=255), nullable=False),
    sa.Column('q2', sa.String(length=255), nullable=False),
    sa.Column('q3', sa.String(length=255), nullable=False),
    sa.Column('q4', sa.String(length=255), nullable=False),
    sa.Column('q5', sa.String(length=255), nullable=False),
    sa.Column('q6', sa.String(length=255), nullable=False),
    sa.Column('q7', sa.String(length=255), nullable=False),
    sa.Column('q8', sa.String(length=255), nullable=False),
    sa.Column('q9', sa.String(length=255), nullable=False),
    sa.Column('q10', sa.String(length=255), nullable=False),
    sa.Column('q11', sa.String(length=255), nullable=False),
    sa.Column('q12', sa.String(length=255), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('points_for_race', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('quiz_answers_history')
    # ### end Alembic commands ###