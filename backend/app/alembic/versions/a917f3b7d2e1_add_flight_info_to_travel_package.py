"""add_flight_info_to_travel_package

Revision ID: a917f3b7d2e1
Revises: f750b46bb4d5
Create Date: 2026-08-19 16:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a917f3b7d2e1"
down_revision: Union[str, Sequence[str], None] = "f750b46bb4d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("travel_package", sa.Column("flight_info", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("travel_package", "flight_info")