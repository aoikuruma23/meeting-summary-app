"""Add LINE OAuth fields to User model

Revision ID: add_line_fields
Revises: add_stripe_fields
Create Date: 2025-08-04 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_line_fields'
down_revision = 'add_stripe_fields'
branch_labels = None
depends_on = None

def upgrade():
    # Add LINE OAuth fields
    op.add_column('users', sa.Column('profile_picture', sa.String(), nullable=True))
    op.add_column('users', sa.Column('auth_provider', sa.String(), nullable=True))
    op.add_column('users', sa.Column('line_user_id', sa.String(), nullable=True))
    
    # Rename line_id to line_user_id if it exists
    try:
        op.alter_column('users', 'line_id', new_column_name='line_user_id')
    except:
        pass  # Column doesn't exist, which is fine

def downgrade():
    # Remove LINE OAuth fields
    op.drop_column('users', 'profile_picture')
    op.drop_column('users', 'auth_provider')
    op.drop_column('users', 'line_user_id') 