from backend.extensions import db

class CommissionRecord(db.Model):
    __tablename__ = 'commission_records'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    # 其他欄位可依需求擴充
