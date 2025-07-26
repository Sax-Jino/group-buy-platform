from extensions import db

class CommissionRecord(db.Model):
    __tablename__ = 'commission_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    # 其他欄位可依需求擴充
