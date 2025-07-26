from backend.extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

class CollaborationProposal(db.Model):
    __tablename__ = 'collaboration_proposals'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    initiator_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), nullable=False, default='draft')  # draft, active, completed, cancelled
    deadline = db.Column(db.DateTime, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    member_requirements = db.Column(JSONB)  # 成員要求（如最低等級等）
    profit_sharing_rules = db.Column(JSONB)  # 分潤規則
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    initiator = db.relationship('User', backref='initiated_proposals')
    product = db.relationship('Product', backref='collaboration_proposals')
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'initiator_id': self.initiator_id,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'status': self.status,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'product_id': self.product_id,
            'member_requirements': self.member_requirements,
            'profit_sharing_rules': self.profit_sharing_rules,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class CollaborationMember(db.Model):
    __tablename__ = 'collaboration_members'
    
    id = db.Column(db.Integer, primary_key=True)
    proposal_id = db.Column(db.Integer, db.ForeignKey('collaboration_proposals.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # leader, member
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, active, left
    contribution_amount = db.Column(db.Float, default=0)
    profit_share_percentage = db.Column(db.Float)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    left_at = db.Column(db.DateTime)
    
    # 關聯
    proposal = db.relationship('CollaborationProposal', backref='members')
    user = db.relationship('User', backref='collaboration_memberships')
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            'id': self.id,
            'proposal_id': self.proposal_id,
            'user_id': self.user_id,
            'role': self.role,
            'status': self.status,
            'contribution_amount': self.contribution_amount,
            'profit_share_percentage': self.profit_share_percentage,
            'joined_at': self.joined_at.isoformat(),
            'left_at': self.left_at.isoformat() if self.left_at else None
        }

class CollaborationTransaction(db.Model):
    __tablename__ = 'collaboration_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    proposal_id = db.Column(db.Integer, db.ForeignKey('collaboration_proposals.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # investment, withdrawal, profit_distribution
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, completed, failed
    transaction_time = db.Column(db.DateTime, default=datetime.utcnow)
    payment_proof = db.Column(db.String(255))  # 付款憑證
    remark = db.Column(db.Text)
    
    # 關聯
    proposal = db.relationship('CollaborationProposal', backref='transactions')
    user = db.relationship('User', backref='collaboration_transactions')
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            'id': self.id,
            'proposal_id': self.proposal_id,
            'user_id': self.user_id,
            'type': self.type,
            'amount': self.amount,
            'status': self.status,
            'transaction_time': self.transaction_time.isoformat(),
            'payment_proof': self.payment_proof,
            'remark': self.remark
        }
