# apps/dataset/models.py
from extensions.ext_database import db
from sqlalchemy.sql import func

class Dataset(db.Model):
    __tablename__ = 'dataset'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)  # 知识库名称
    desc = db.Column(db.String(200), nullable=False)  # 知识库描述
    created_at = db.Column(db.DateTime, nullable=True, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=True, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'<Dataset {self.id}, {self.name}>'
    


# apps/dataset/models.py
class Document(db.Model):
    __tablename__ = 'document'

    __table_args__ = (
        db.Index('idx_document_dataset_id', 'dataset_id'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dataset_id = db.Column(db.Integer, nullable=False)
    file_name = db.Column(db.String(100), nullable=False)  # 文件名称
    file_path = db.Column(db.String(100), nullable=False)  # 文件路径
    status = db.Column(db.String(100), nullable=False)  # 状态
    created_at = db.Column(db.DateTime, nullable=True, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=True, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'<Document {self.id}, {self.file_name}>'
    

# apps/dataset/models.py
class Segment(db.Model):
    __tablename__ = 'segment'

    __table_args__ = (
        db.Index('idx_segment_dataset_id', 'dataset_id'),
        db.Index('idx_segment_document_id', 'document_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, nullable=False)
    document_id = db.Column(db.Integer, nullable=False)
    order = db.Column(db.Integer, nullable=False)  # 顺序
    content = db.Column(db.Text, nullable=False)  # 内容
    status = db.Column(db.String(100), nullable=False)  # 状态
    created_at = db.Column(db.DateTime, nullable=True, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=True, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'<Segment {self.id}, {self.content[:20]}>'