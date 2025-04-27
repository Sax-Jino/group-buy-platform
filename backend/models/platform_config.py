from extensions import db
from datetime import datetime

class PlatformConfig(db.Model):
    __tablename__ = 'platform_configs'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), nullable=False, unique=True)  # points_enabled
    value = db.Column(db.String(100), nullable=False)  # true/false
    updated_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def get_value(cls, key, default=None):
        config = cls.query.filter_by(key=key).first()
        return config.value if config else default

    @classmethod
    def set_value(cls, key, value):
        config = cls.query.filter_by(key=key).first()
        if config:
            config.value = value
            config.updated_at = datetime.utcnow()
        else:
            config = cls(key=key, value=value, updated_at=datetime.utcnow())
            db.session.add(config)
        db.session.commit()