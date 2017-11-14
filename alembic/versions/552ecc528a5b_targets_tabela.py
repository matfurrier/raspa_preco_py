"""Targets tabela

Revision ID: 552ecc528a5b
Revises: ba84e6db3bcd
Create Date: 2017-11-14 15:07:42.111818

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '552ecc528a5b'
down_revision = 'ba84e6db3bcd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('targets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('target', sa.String(length=50), nullable=True),
    sa.Column('attributes', sa.String(length=100), nullable=True),
    sa.Column('getter', sa.String(length=20), nullable=True),
    sa.Column('site_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_column('sites', 'targets')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sites', sa.Column('targets', sa.BLOB(), nullable=True))
    op.drop_table('targets')
    # ### end Alembic commands ###
