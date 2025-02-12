# tasks/dateset_document_split_task.py
from celery import shared_task
import os
import fitz  # PyMuPDF
import docx  # python-docx
import pandas as pd  # pandas库
from apps.dataset.models import Document, Segment
from config import *
from helper import segment_text
from extensions.ext_database import db
from .dataset_segment_embed_task import task as dataset_segment_embed_task



def process_pdf(file_path):
    # 读取PDF文件内容
    doc = fitz.open(file_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    # 将文本分段
    return segment_text(text, SEGMENT_LENGTH, OVERLAP)

def process_txt(file_path):
    with open(file_path, encoding='utf-8') as file:
        text = file.read()
    return segment_text(text, SEGMENT_LENGTH, OVERLAP)

def process_word(file_path):
    doc = docx.Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return segment_text(text, SEGMENT_LENGTH, OVERLAP)

def process_csv(file_path):
    df = pd.read_csv(file_path)
    data = []
    for _, row in df.iterrows():
        row_str = ', '.join([f"{col}: {row[col]}" for col in df.columns])
        data.append(row_str)
    return data

def process_excel(file_path):
    df = pd.read_excel(file_path)
    data = []
    for _, row in df.iterrows():
        row_str = ', '.join([f"{col}: {row[col]}" for col in df.columns])
        data.append(row_str)
    return data

def load_and_split(file_path):
    _, file_extension = os.path.splitext(file_path)
    file_ext = file_extension[1:]
    # 按后缀分开处理
    if file_ext == 'pdf':
        return process_pdf(file_path)
    if file_ext == 'txt':
        return process_txt(file_path)
    if file_ext == 'docx':
        return process_word(file_path)
    if file_ext == 'csv':
        return process_csv(file_path)
    if file_ext == 'xlsx':
        return process_excel(file_path)
    return []

@shared_task(queue='dataset')
def task(document_id):
    document = Document.query.filter_by(id=document_id).first()
    # 加载并分割文件
    file_path = os.path.join(UPLOAD_FOLDER, document.file_path)
    segments = load_and_split(file_path)

    try:
        # 存储片段
        for i, content in enumerate(segments):
            # 附加文档信息，仅供参考
            content = f'文件《{document.file_name}》，第{i+1}段，内容如下：\n{content}'
            new_segment = Segment(
                dataset_id = document.dataset_id,
                document_id = document.id,
                order = i + 1,
                content = content,
                status = 'init'
            )
            db.session.add(new_segment)
        # 修改文档撞他
        document.status = 'indexing'

        # 发起建立索引任务，延迟10秒，等下面事物还先提交
        dataset_segment_embed_task.apply_async(
            kwargs = {'document_id': document_id},
            countdown = 10
        )


        db.session.commit()


        print('exec dataset_document_split_task success.')
    except Exception as e:
        db.session.rollback()
        print(f'exec dataset_document_split_task error. {e}')