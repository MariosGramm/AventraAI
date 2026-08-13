"""add_freemium_google_fields

Revision ID: f750b46bb4d5
Revises: 6b5d796b0d3d
Create Date: 2026-08-12 17:14:52.205044

"""
from typing import Sequence, Union
import sqlmodel
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f750b46bb4d5'
down_revision: Union[str, Sequence[str], None] = '6b5d796b0d3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE triptype AS ENUM ('SOLO', 'FAMILY', 'ROMANTIC', 'FRIENDS')")
    op.execute("CREATE TYPE subscriptiontier AS ENUM ('FREE', 'PAID')")
    op.execute("CREATE TYPE authprovider AS ENUM ('GOOGLE', 'EMAIL')")

    op.add_column('search_session', sa.Column('adults', sa.Integer(), nullable=False, server_default='2'))
    op.add_column('search_session', sa.Column('children', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('search_session', sa.Column('trip_type', sa.Enum('SOLO', 'FAMILY', 'ROMANTIC', 'FRIENDS', name='triptype'), nullable=True))

    op.add_column('user', sa.Column('subscription_tier', sa.Enum('FREE', 'PAID', name='subscriptiontier'), nullable=False, server_default='FREE'))
    op.add_column('user', sa.Column('monthly_searches_used', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('user', sa.Column('searches_reset_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('user', sa.Column('google_id', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True))
    op.add_column('user', sa.Column('auth_provider', sa.Enum('GOOGLE', 'EMAIL', name='authprovider'), nullable=False, server_default='EMAIL'))


def downgrade() -> None:
    op.drop_column('search_session', 'trip_type')
    op.drop_column('search_session', 'adults')
    op.drop_column('search_session', 'children')
    op.drop_column('user', 'auth_provider')
    op.drop_column('user', 'google_id')
    op.drop_column('user', 'searches_reset_date')
    op.drop_column('user', 'monthly_searches_used')
    op.drop_column('user', 'subscription_tier')

    op.execute("DROP TYPE IF EXISTS triptype")
    op.execute("DROP TYPE IF EXISTS subscriptiontier")
    op.execute("DROP TYPE IF EXISTS authprovider")
