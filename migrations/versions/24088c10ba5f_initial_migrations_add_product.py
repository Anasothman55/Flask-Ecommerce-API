"""Initial migrations add product

Revision ID: 24088c10ba5f
Revises: ddddd0acfcac
Create Date: 2024-10-16 13:29:08.785199

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24088c10ba5f'
down_revision = 'ddddd0acfcac'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_constraint('products_topic_ids_fkey', type_='foreignkey')
        batch_op.drop_column('topic_ids')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('topic_ids', sa.UUID(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('products_topic_ids_fkey', 'topics', ['topic_ids'], ['id'])

    # ### end Alembic commands ###
