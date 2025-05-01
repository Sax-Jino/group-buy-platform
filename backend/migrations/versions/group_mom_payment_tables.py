"""add group mom and payment tables

Revision ID: group_mom_payment_tables
Revises: settlement_tables
Create Date: 2025-05-01 09:30:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision = 'group_mom_payment_tables'
down_revision = 'settlement_tables'
branch_labels = None
depends_on = None

def upgrade():
    # 建立團媽等級表
    op.create_table(
        'group_mom_levels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('min_downline', sa.Integer(), default=0),
        sa.Column('commission_rate', sa.Float(), nullable=False),
        sa.Column('quarterly_fee', sa.Float(), nullable=False),
        sa.Column('semi_annual_fee', sa.Float(), nullable=False),
        sa.Column('annual_fee', sa.Float(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 建立付款表
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('proof', sa.String(255)),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('payment_method', sa.String(20)),
        sa.Column('bank_code', sa.String(10)),
        sa.Column('account_last5', sa.String(5)),
        sa.Column('payment_time', sa.DateTime()),
        sa.Column('approved_at', sa.DateTime()),
        sa.Column('approved_by', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('rejected_at', sa.DateTime()),
        sa.Column('rejected_by', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('rejection_reason', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 修改用戶表，增加團媽相關欄位
    op.add_column('users', sa.Column('group_mom_fee_paid_until', sa.DateTime()))
    op.add_column('users', sa.Column('status_history', JSON))

def downgrade():
    # 刪除表格和欄位
    op.drop_column('users', 'status_history')
    op.drop_column('users', 'group_mom_fee_paid_until')
    op.drop_table('payments')
    op.drop_table('group_mom_levels')