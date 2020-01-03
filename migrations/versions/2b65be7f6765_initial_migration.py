"""initial_migration

Revision ID: 2b65be7f6765
Revises: 
Create Date: 2019-12-31 19:39:22.081601

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2b65be7f6765'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('roles', sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.String(length=64), nullable=True),
                    sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('name'))
    op.create_table('users', sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('username', sa.String(length=64), nullable=True),
                    sa.Column('role_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['role_id'],
                        ['roles.id'],
                    ), sa.PrimaryKeyConstraint('id'))
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')
    op.drop_table('roles')
