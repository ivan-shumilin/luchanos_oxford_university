"""category

Revision ID: 339991d0675c
Revises: 6ed872653d9c
Create Date: 2024-05-22 21:19:53.089621

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '339991d0675c'
down_revision = '6ed872653d9c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('position', sa.Column('category_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'position', 'category', ['category_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'position', type_='foreignkey')
    op.drop_column('position', 'category_id')
    op.drop_table('category')
    # ### end Alembic commands ###
