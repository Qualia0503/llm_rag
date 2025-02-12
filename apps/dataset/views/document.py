# apps/dataset/views/document.py
import os, uuid
from flask import request, render_template, redirect, url_for, flash
from extensions.ext_database import db
from config import *
from .. import bp
from ..models import Dataset, Document, Segment
from helper import allowed_file
from tasks.dataset_document_split_task import task as dataset_document_split_task
from ..milvus_models import DatasetMilvusModel




@bp.route("/document_list/<int:dataset_id>", endpoint="document_list")
def list(dataset_id):
    dataset = Dataset.query.filter_by(id=dataset_id).first()
    # 处理分页逻辑
    page = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = Document.query.filter_by(
        dataset_id=dataset_id
        ).order_by(Document.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    documents = pagination.items
    return render_template("dataset/document_list.html", 
                           dataset=dataset, 
                           documents=documents,
                           pagination=pagination)



# apps/dataset/views/document.py
@bp.route("/document_create/<int:dataset_id>", methods=["GET", "POST"], endpoint="document_create")
def create(dataset_id):
    dataset = Dataset.query.filter_by(id=dataset_id).first()
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            if not allowed_file(file.filename):
                flash("文件格式不支持。只允许以下类型：" + ', '.join(ALLOWED_EXTENSIONS), "error")
            elif file.content_length > MAX_CONTENT_LENGTH:
                flash("文件大小超过限制。最大允许16MB。", "error")
            else:
                try:
                    # 提取文件扩展名
                    file_ext = os.path.splitext(file.filename)[1]
                    # print(file_ext)
                    # raise Exception("测试异常1")
                    # 生成新的文件名
                    file_path = f"{uuid.uuid4()}{file_ext}"
                    # print(file_path)
                    # raise Exception("测试异常2")
                    # 保存文件
                    file.save(os.path.join(UPLOAD_FOLDER, file_path))

                    # 保存数据
                    new_document = Document(
                        dataset_id=dataset_id,
                        file_name=file.filename,
                        file_path=file_path,
                        status='init'
                    )
                    db.session.add(new_document)
                    db.session.commit()

                    # 发起文件分割任务

                    dataset_document_split_task.delay(new_document.id)

                    flash("文件上传成功", "success")
                    return redirect(url_for("dataset.document_list", dataset_id=dataset_id))
                except Exception as e:
                    db.session.rollback()
                    flash(f"文件上传失败: {e}", "error")
        else:
            flash("请选择文件", "error")
    # 渲染页面
    return render_template("dataset/document_create.html", dataset=dataset)


@bp.route("/document_delete/<int:document_id>", endpoint="document_delete")
def delete(document_id):
    document = Document.query.filter_by(id=document_id).first()
    try:

        # 删除本地文件
        file_full_path = os.path.join(UPLOAD_FOLDER, document.file_path)
        if os.path.exists(file_full_path):
            os.remove(file_full_path)

        Document.query.filter_by(id=document_id).delete()
        Segment.query.filter_by(document_id=document_id).delete()
        
        # 删除 milvus 数据
        # 删除 milvus 数据
        delete_expr = f'document_id == {document_id}'
        DatasetMilvusModel.delete(delete_expr)
            
        # 提交事务
        db.session.commit()
        
        flash("文档删除成功", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"操作失败: {e}", "error")
    return redirect(url_for("dataset.document_list", dataset_id=document.dataset_id))