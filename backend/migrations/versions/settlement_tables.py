"""add settlement tables

Revision ID: settlement_tables
Revises: previous_revision
Create Date: 2025-05-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision = 'settlement_tables'
down_revision = 'previous_revision'  # 請替換為實際的上一個版本
branch_labels = None
depends_on = None

def upgrade():
    # 建立結算表
    op.create_table(
        'settlements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('period', sa.String(8), nullable=False),
        sa.Column('settlement_type', sa.String(20), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('commission_amount', sa.Float()),
        sa.Column('tax_amount', sa.Float()),
        sa.Column('net_amount', sa.Float(), nullable=False),
        sa.Column('order_count', sa.Integer(), nullable=False),
        sa.Column('order_details', JSON),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('is_confirmed', sa.Boolean(), server_default='false'),
        sa.Column('confirmed_at', sa.DateTime()),
        sa.Column('paid_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )

    # 建立未結算訂單表
    op.create_table(
        'unsettled_orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('orders.id'), nullable=False),
        sa.Column('expected_settlement_date', sa.DateTime(), nullable=False),
        sa.Column('max_retention_date', sa.DateTime(), nullable=False),
        sa.Column('alert_level', sa.String(10), server_default='normal'),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )

    # 建立結算對帳單表
    op.create_table(
        'settlement_statements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('settlement_id', sa.Integer(), sa.ForeignKey('settlements.id'), nullable=False),
        sa.Column('statement_type', sa.String(20), nullable=False),
        sa.Column('period', sa.String(8), nullable=False),
        sa.Column('total_orders', sa.Integer(), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('commission_details', JSON),
        sa.Column('tax_details', JSON),
        sa.Column('shipping_details', JSON),
        sa.Column('return_deductions', JSON),
        sa.Column('dispute_deadline', sa.DateTime(), nullable=False),
        sa.Column('is_disputed', sa.Boolean(), server_default='false'),
        sa.Column('dispute_details', JSON),
        sa.Column('is_finalized', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )

    # 添加訂單表的新欄位
    op.add_column('orders', sa.Column('cost', sa.Float()))
    op.add_column('orders', sa.Column('profit_calculated_at', sa.DateTime()))
    op.add_column('orders', sa.Column('settled_at', sa.DateTime()))
    op.add_column('orders', sa.Column('profit_breakdown', JSON))
    op.add_column('orders', sa.Column('profit_distribution_log', JSON))
    op.add_column('orders', sa.Column('tax_amount', sa.Float()))
    op.add_column('orders', sa.Column('tax_status', sa.String(20), server_default='pending'))
    op.add_column('orders', sa.Column('tax_paid_at', sa.DateTime()))
    op.add_column('orders', sa.Column('platform_fee', sa.Float()))
    op.add_column('orders', sa.Column('supplier_fee', sa.Float()))
    op.add_column('orders', sa.Column('platform_profit', sa.Float()))
    op.add_column('orders', sa.Column('supplier_amount', sa.Float()))
    op.add_column('orders', sa.Column('supplier_paid', sa.Boolean(), server_default='false'))
    op.add_column('orders', sa.Column('supplier_paid_at', sa.DateTime()))

def downgrade():
    # 刪除結算相關表
    op.drop_table('settlement_statements')
    op.drop_table('unsettled_orders')
    op.drop_table('settlements')
    
    # 移除訂單表的新欄位
    op.drop_column('orders', 'supplier_paid_at')
    op.drop_column('orders', 'supplier_paid')
    op.drop_column('orders', 'supplier_amount')
    op.drop_column('orders', 'platform_profit')
    op.drop_column('orders', 'supplier_fee')
    op.drop_column('orders', 'platform_fee')
    op.drop_column('orders', 'tax_paid_at')
    op.drop_column('orders', 'tax_status')
    op.drop_column('orders', 'tax_amount')
    op.drop_column('orders', 'profit_distribution_log')
    op.drop_column('orders', 'profit_breakdown')
    op.drop_column('orders', 'settled_at')
    op.drop_column('orders', 'profit_calculated_at')
    op.drop_column('orders', 'cost')