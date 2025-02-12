

# commands/test_dataset_document_split_task.py
import click
import os
import fitz  # PyMuPDF
import docx  # python-docx
import pandas as pd  # pandas库
from apps.dataset.models import Document, Segment
from config import *
from helper import segment_text
from extensions.ext_database import db

@click.command("test_dataset_document_split_task")
def run():
    document_id = 6
    document = Document.query.filter_by(id=document_id).first()
    # 加载并分割文件
    file_path = os.path.join(UPLOAD_FOLDER, document.file_path)
    # print(file_path)
    # exit()
    segments = load_and_split(file_path)
    # print(len(segments))
    # exit()
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
        # 修改文档状态
        document.status = 'indexing'
        db.session.commit()
        print('exec dateset_document_split_task success.')
    except Exception as e:
        db.session.rollback()
        print(f'exec dateset_document_split_task error. {e}')


############################################################################################################
def load_and_split(file_path):
    _, file_extension = os.path.splitext(file_path)
    # print(_, file_extension)
    # exit()
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
###############################################################
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

############################################################