# tasks/dataset_segment_embed_task.py
from celery import shared_task
import os
from apps.dataset.models import Document, Segment
from config import *
from extensions.ext_database import db
from helper import get_llm_embedding
from apps.dataset.milvus_models import DatasetMilvusModel


@shared_task(queue='dataset')
def task(document_id=None, segment_id=None):
    # 整个文档创建索引
    try:
        if document_id:
            document = Document.query.filter_by(id=document_id).first()
            segments = Segment.query.filter_by(document_id=document_id).all()
            
            # 删除document_id对应Milvus数据
            delete_expr = f'document_id == {document_id}'
            DatasetMilvusModel.delete(delete_expr)

            # 存储片段
            for i, segment in enumerate(segments):
                # 获取句向量并存储
                response = get_llm_embedding(segment.content)
                text_vector = response.data[0].embedding
                DatasetMilvusModel.insert([{
                    'dataset_id': segment.dataset_id,
                    'document_id': segment.document_id,
                    'segment_id': segment.id,
                    'text_vector': text_vector
                }])
                # 修改片段状态
                segment.status = 'completed'

            # 更新文档状态
            document.status = 'completed'
            db.session.commit()
            print('exec dataset_segment_embed_task success.')
        
        # 插入或更新片段
        if segment_id:
            segment = Segment.query.filter_by(id=segment_id).first()
            # 删除segment_id对应Milvus数据
            delete_expr = f'segment_id == {segment_id}'
            DatasetMilvusModel.delete(delete_expr)
            # 获取句向量并存储
            response = get_llm_embedding(segment.content)
            text_vector = response.data[0].embedding
            DatasetMilvusModel.insert([{
                'dataset_id': segment.dataset_id,
                'document_id': segment.document_id,
                'segment_id': segment.id,
                'text_vector': text_vector
            }])
            # 修改片段状态
            segment.status = 'completed'
            db.session.commit()
            print('exec dataset_segment_embed_task success.')

    except Exception as e:
        db.session.rollback()
        print(f'exec dataset_segment_embed_task error. {e}')