"""Initial migrations add topic

Revision ID: 426e9bec0bba
Revises: a42c07488885
Create Date: 2024-10-01 21:29:12.393964

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '426e9bec0bba'
down_revision = 'a42c07488885'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('topics', schema=None) as batch_op:
        batch_op.drop_constraint('topics_name_key', type_='unique')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('topics', schema=None) as batch_op:
        batch_op.create_unique_constraint('topics_name_key', ['name'])

    # ### end Alembic commands ###
