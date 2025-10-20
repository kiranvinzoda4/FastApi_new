"""quantity changed

Revision ID: d7900525b363
Revises: c8a1f93119e4
Create Date: 2025-07-08 22:02:16.128808
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd7900525b363'
down_revision = 'c8a1f93119e4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'carts',
        sa.Column(
            'unit_type',
            sa.Enum('gram', 'kg', 'piece', name='unittypeenum'),
            nullable=False,
            server_default='kg'  # <-- default set
        )
    )

    op.alter_column(
        'carts',
        'quantity',
        existing_type=mysql.INTEGER(),
        type_=sa.Numeric(precision=10, scale=2),
        existing_nullable=False
    )

    op.add_column(
        'order_items',
        sa.Column(
            'unit_type',
            sa.Enum('gram', 'kg', 'piece', name='unittypeenum'),
            nullable=False,
            server_default='kg'  # <-- default set
        )
    )

    op.alter_column(
        'order_items',
        'quantity',
        existing_type=mysql.INTEGER(),
        type_=sa.Numeric(precision=10, scale=2),
        existing_nullable=False
    )

    op.alter_column(
        'vegetables',
        'quantity',
        existing_type=mysql.INTEGER(),
        type_=sa.Numeric(precision=10, scale=2),
        existing_nullable=False
    )


def downgrade():
    op.alter_column(
        'vegetables',
        'quantity',
        existing_type=sa.Numeric(precision=10, scale=2),
        type_=mysql.INTEGER(),
        existing_nullable=False
    )

    op.alter_column(
        'order_items',
        'quantity',
        existing_type=sa.Numeric(precision=10, scale=2),
        type_=mysql.INTEGER(),
        existing_nullable=False
    )

    op.drop_column('order_items', 'unit_type')

    op.alter_column(
        'carts',
        'quantity',
        existing_type=sa.Numeric(precision=10, scale=2),
        type_=mysql.INTEGER(),
        existing_nullable=False
    )

    op.drop_column('carts', 'unit_type')
