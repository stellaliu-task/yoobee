"""add total_fee to bookings and fee to booking_extras

Revision ID: 6804eb3d9bd1
Revises: 4a99c7a7d7bb
Create Date: 2024-06-08

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '6804eb3d9bd1'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('bookings', sa.Column('total_fee', sa.DECIMAL(10, 2), nullable=False, server_default='0'))
    

def downgrade() -> None:
    
    op.drop_column('bookings', 'total_fee') 