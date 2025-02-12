import os

from flask import request, render_template, redirect, url_for, flash
from extensions.ext_database import db
from sqlalchemy.sql import func
from config import UPLOAD_FOLDER
from ..models import Dataset, Document, Segment
from .. import bp
from ..forms import DatasetForm
from ..milvus_models import DatasetMilvusModel


@bp.route("/", endpoint="dataset_list")
def list():
    datasets = (
        db.session.query(
            Dataset.id,
            Dataset.name,
            Dataset.desc,
            Dataset.created_at,
            func.count(Document.id).label("document_count"),
        )
        .outerjoin(Document, Dataset.id == Document.dataset_id)
        .group_by(Dataset.id)
        .order_by(Dataset.id.desc())
        .all()
    )
    return render_template("dataset/dataset_list.html", datasets=datasets)



@bp.route("/dataset_create", methods=['GET', 'POST'], endpoint="dataset_create")
def create():
    form = DatasetForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        desc = form.desc.data
        # name = request.form.get('name')
        # desc = request.form.get('desc')

        # 创建 Dataset 实例并插入数据
        new_dataset = Dataset(name=name, desc=desc)
        db.session.add(new_dataset)
        db.session.commit()

        flash("知识库创建成功!", "success")
        return redirect(url_for("dataset.dataset_list"))
    else:
        if form.errors:
            msg = ' '.join([val for values in form.errors.values() for val in values])
            flash(msg, 'error')

    return render_template('dataset/dataset_create.html', form=form)



@bp.route("/dataset_edit/<int:dataset_id>", methods=["GET", "POST"], endpoint="dataset_edit")
def edit(dataset_id):
    form = DatasetForm(request.form)
    # 查询单条 dataset 数据
    dataset = Dataset.query.filter_by(id=dataset_id).first()

    if request.method == 'POST' and form.validate():
        name = form.name.data
        desc = form.desc.data
        # name = request.form.get('name')
        # desc = request.form.get('desc')

        # 创建 Dataset 实例并插入数据
        dataset.name = name
        dataset.desc = desc
        db.session.commit()

        flash("知识库修改成功!", "success")
        return redirect(url_for("dataset.dataset_list"))
    else:
        if form.errors:
            msg = ' '.join([val for values in form.errors.values() for val in values])
            flash(msg, 'error')

    return render_template("dataset/dataset_edit.html", dataset=dataset, form=form)


@bp.route("/dataset_delete/<int:dataset_id>", endpoint="dataset_delete")
def delete(dataset_id):
    try:
        documents = Document.query.filter_by(dataset_id=dataset_id).all()
        # 删除本地文件
        for document in documents:
            file_full_path = os.path.join(UPLOAD_FOLDER, document.file_path)
            if os.path.exists(file_full_path):
                os.remove(file_full_path)

        Dataset.query.filter_by(id=dataset_id).delete()
        Document.query.filter_by(dataset_id=dataset_id).delete()
        Segment.query.filter_by(dataset_id=dataset_id).delete()
        
        # 删除 milvus 数据
        delete_expr = f'dataset_id == {dataset_id}'
        DatasetMilvusModel.delete(delete_expr)

        
        # 提交事务
        db.session.commit()

        flash("知识库删除成功", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"操作失败: {e}", "error")

    return redirect(url_for("dataset.dataset_list"))