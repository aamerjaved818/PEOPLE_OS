"""Add report schedules table

Revision ID: 001_add_report_schedules
Revises: 
Create Date: 2026-01-23 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql, sqlite

# revision identifiers, used by Alembic.
revision = '001_add_report_schedules'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ReportSchedule table
    op.create_table(
        'report_schedules',
        sa.Column('id', sa.String(36), nullable=False, primary_key=True),
        sa.Column('user_id', sa.String(255), nullable=False, index=True),
        sa.Column('report_name', sa.String(255), nullable=False),
        sa.Column('report_type', sa.String(50), nullable=False),
        sa.Column('format', sa.String(50), nullable=False),
        sa.Column('frequency', sa.String(50), nullable=False),
        sa.Column('cron_expression', sa.String(255), nullable=False),
        sa.Column('recipients', sa.JSON(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('include_summary', sa.Boolean(), default=True),
        sa.Column('is_active', sa.Boolean(), default=True, index=True),
        sa.Column('last_run', sa.DateTime(), nullable=True),
        sa.Column('next_run', sa.DateTime(), nullable=False),
        sa.Column('job_id', sa.String(255), nullable=True, unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create indices
    op.create_index('idx_report_schedules_user_id', 'report_schedules', ['user_id'])
    op.create_index('idx_report_schedules_is_active', 'report_schedules', ['is_active'])
    op.create_index('idx_report_schedules_next_run', 'report_schedules', ['next_run'])
    op.create_index('idx_report_schedules_job_id', 'report_schedules', ['job_id'])


def downgrade() -> None:
    # Drop indices
    op.drop_index('idx_report_schedules_job_id')
    op.drop_index('idx_report_schedules_next_run')
    op.drop_index('idx_report_schedules_is_active')
    op.drop_index('idx_report_schedules_user_id')
    
    # Drop table
    op.drop_table('report_schedules')
