"""自動建立唯一 SUPERADMIN JackeyChen 帳號

Revision ID: 20250602_create_superadmin_jackeychen
Revises: group_mom_payment_tables
Create Date: 2025-06-02
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

# revision identifiers, used by Alembic.
revision = '20250602_create_superadmin_jackeychen'
down_revision = 'group_mom_payment_tables'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        User = sa.table('users',
            sa.column('id', sa.Integer),
            sa.column('username', sa.String),
            sa.column('email', sa.String),
            sa.column('password_hash', sa.String),
            sa.column('role', sa.String),
            sa.column('is_active', sa.Boolean),
            sa.column('created_at', sa.DateTime),
        )
        # 刪除所有 superadmin
        session.execute(sa.text("DELETE FROM users WHERE role='superadmin' AND username!='JackeyChen'"))
        # 檢查 JackeyChen 是否已存在
        result = session.execute(sa.text("SELECT id FROM users WHERE role='superadmin' AND username='JackeyChen'"))
        if not result.first():
            # 建立唯一 superadmin
            session.execute(User.insert().values(
                username='JackeyChen',
                email='jackeychen@admin.com',
                password_hash=generate_password_hash('JackeyChen@2025'),
                role='superadmin',
                is_active=True,
                created_at=sa.func.now()
            ))
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        session.execute(sa.text("DELETE FROM users WHERE role='superadmin' AND username='JackeyChen'"))
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
