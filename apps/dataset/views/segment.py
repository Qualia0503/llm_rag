from flask import render_template, request, redirect, url_for, flash
from extensions.ext_database import db
from ..models import Dataset, Document, Segment
from .. import bp
from ..forms import SegmentForm
from tasks.dataset_segment_embed_task import task as dataset_segment_embed_task
from ..milvus_models import DatasetMilvusModel


@bp.route("/segment/<int:document_id>", endpoint="segment_list")
def segment_list(document_id):
    document = Document.query.filter_by(id=document_id).first()
    dataset = Dataset.query.filter_by(id=document.dataset_id).first()
    segments = Segment.query.filter_by(document_id=document_id).order_by(Segment.order.asc()).all()
    return render_template("dataset/segment_list.html", segments=segments, document=document, dataset=dataset)


#############################
@bp.route("/segment_create/<int:document_id>", methods=["GET", "POST"], endpoint="segment_create")
def create(document_id):
    document = Document.query.filter_by(id=document_id).first()
    # 处理表单数据
    form = SegmentForm(request.form)
    if request.method == "POST" and form.validate():
        content = form.content.data
        order = form.order.data
        new_segment = Segment(
            dataset_id = document.dataset_id,
            document_id = document_id,
            content = content,
            order = order,
            status = 'init',
        )
        db.session.add(new_segment)
        db.session.commit()

        dataset_segment_embed_task.delay(None, new_segment.id)

        flash("片段插入成功!", "success")
        return redirect(url_for("dataset.segment_list", document_id=document.id))
    else:
        if form.errors:
            error_msg = ' '.join([error[0] for error in form.errors.values()])
            flash(error_msg, "error")
    # 渲染页面
    return render_template("dataset/segment_create.html", document=document, form=form)


###########################

@bp.route("/segment_edit/<int:segment_id>", methods=["GET", "POST"], endpoint="segment_edit")
def edit(segment_id):
    segment = Segment.query.filter_by(id=segment_id).first()
    document = Document.query.filter_by(id=segment.document_id).first()
    # 处理表单数据
    form = SegmentForm(request.form)
    if request.method == "POST" and form.validate():
        segment.content = form.content.data
        segment.order = form.order.data
        segment.status = 'init'
        db.session.commit()
        dataset_segment_embed_task.delay(None, segment.id)

        flash("知识库修改成功!", "success")
        return redirect(url_for("dataset.segment_list", document_id=document.id))
    else:
        if form.errors:
            error_msg = ' '.join([error[0] for error in form.errors.values()])
            flash(error_msg, "error")
    return render_template("dataset/segment_edit.html", document=document, segment=segment, form=form)


#############################

@bp.route("/segment_delete/<int:segment_id>", endpoint="segment_delete")
def delete(segment_id):
    segment = Segment.query.filter_by(id=segment_id).first()
    try:
        
        Segment.query.filter_by(id=segment_id).delete()
        
        # 删除 milvus 数据
        delete_expr = f'segment_id == {segment_id}'
        DatasetMilvusModel.delete(delete_expr)
                
        # 提交事务
        db.session.commit()

        flash("片段删除成功", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"操作失败: {e}", "error")

    return redirect(url_for("dataset.segment_list", document_id=segment.document_id))