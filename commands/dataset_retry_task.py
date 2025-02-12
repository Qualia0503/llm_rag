import click
from apps.dataset.models import Document, Segment
from tasks.dataset_document_split_task import task as dataset_document_split_task
from tasks.dataset_segment_embed_task import task as dataset_segment_embed_task

@click.command("dataset_retry_task")
def run():
    # 文档分割重试
    documents = Document.query.filter_by(status='init').all()
    for document in documents:
        dataset_document_split_task.delay(document.id)

    # 文档建立索引重试
    documents = Document.query.filter_by(status='indexing').all()
    for document in documents:
        dataset_segment_embed_task.delay(document.id)

    # 片段创建索引重试
    segments = Segment.query.filter_by(status='init').all()
    for segment in segments:
        dataset_segment_embed_task.delay(None, segment.id)

    click.echo("[command] dataset_retry_task success.")