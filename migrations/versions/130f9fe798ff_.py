"""empty message

Revision ID: 130f9fe798ff
Revises: 522bf97233a6
Create Date: 2020-05-24 21:34:08.788401

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '130f9fe798ff'
down_revision = '522bf97233a6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('task_chunk_task_id_fkey', 'task_chunk', type_='foreignkey')
    op.create_foreign_key(None, 'task_chunk', 'task', ['task_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'task_chunk', type_='foreignkey')
    op.create_foreign_key('task_chunk_task_id_fkey', 'task_chunk', 'task', ['task_id'], ['id'])
    # ### end Alembic commands ###
