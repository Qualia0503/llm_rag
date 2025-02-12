# apps/chat/models.py
from extensions.ext_database import db
from sqlalchemy.sql import func

class Conversation(db.Model):
    __tablename__ = 'conversation'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.String(50), nullable=False)  # 对话标识
    name = db.Column(db.String(50), nullable=False)  # 对话名称
    messages = db.Column(db.JSON, nullable=False)  # 对话内容
    created_at = db.Column(db.DateTime, nullable=True, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=True, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'<Conversation {self.id}, {self.name}>'

