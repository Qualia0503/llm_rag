# apps/chat/views.py
import time
from flask import render_template, request, Response
from extensions.ext_database import db
from . import bp
from config import LLM_MODELS
from apps.dataset.models import Dataset
from helper import *
from .services import retrieve_related_texts
from .models import Conversation




@bp.route('/', endpoint='index')
def index():
    dataset_objs = Dataset.query.order_by(Dataset.id.desc()).all()
    conversation_objs = Conversation.query.with_entities(
        Conversation.id, Conversation.uid, Conversation.name
    ).order_by(Conversation.id.desc()).all()

    data = {
        'llm_models': list(LLM_MODELS.keys()),
        'datasets': [{'id': obj.id, 'name': obj.name} for obj in dataset_objs],
        'conversations': [{'uid': obj.uid, 'name': obj.name} for obj in conversation_objs],
    }
    return render_template('chat/index.html', **data)


@bp.route('/test', methods=['POST'])
def test():
    output = '这是模拟的一段大模型输出的文字'
    def generate():
        full_text = ''
        # 逐词输出内容
        for chunk in output:
            time.sleep(1)
            content = chunk
            if content:
                full_text += content
                yield 'data: ' + json_response(200, 'ok', {
                    'content': content,
                    'text': full_text
                }) + '\n\n'
    return Response(generate(), content_type='text/plain')


@bp.route('/completions', methods=['POST'], endpoint='completions')
def completions():
    # 接收参数
    data = request.get_json()
    messages = data['messages']
    params = data['params']

    # 如果选中知识库，追加召回文本
    if params['dataset_ids']:
    # 相似文本召回，并添加到messages中
        messages = retrieve_related_texts(messages, params)

    # 请求大模型
    completion = get_llm_chat(messages[:10], params['model_name'], True)
    # 定义生成器
    def generate():
        full_text = ''
        # 逐词输出内容
        for chunk in completion:
            # print("Chunk:", chunk)
            # if not chunk.choices or len(chunk.choices) == 0:
            #     continue
            ############这里非常重要，Azure OpenAI 返回的数据结构和 OpenAI 返回的数据结构不一样，需要做不同的处理############
            ############Azure的第一个返回的值是空值，如果不做判断，会导致程序异常，第一个返回的是空值，第二个返回的是有值的############
            if not chunk.choices:
                continue
            content = chunk.choices[0].delta.content
            if content:
                full_text += content
                yield 'data: ' + json_response(200, 'ok', {
                    'content': content,
                    'text': full_text
                }) + '\n\n'
    return Response(generate(), content_type='text/plain')


@bp.route('/conversation_create', methods=['POST'], endpoint='conversation_create')
def conversation_create():
    try:
        data = request.get_json()
        new_conversation = Conversation(
            uid = data['uid'],
            name = data['name'],
            messages = []
        )
        db.session.add(new_conversation)
        db.session.commit()
        return json_response(200, 'ok')
    except Exception as e:
        return json_response(500, f'error: {e}')
    

@bp.route('/conversation_delete', methods=['POST'], endpoint='conversation_delete')
def conversation_delete():
    try:
        data = request.get_json()
        conversation = Conversation.query.filter_by(
            uid = data['uid'],
        ).first()
        db.session.delete(conversation)
        db.session.commit()
        return json_response(200, 'ok')
    except Exception as e:
        return json_response(500, f'error: {e}')
    

@bp.route('/conversation_edit', methods=['POST'], endpoint='conversation_edit')
def conversation_edit():
    try:
        data = request.get_json()
        conversation = Conversation.query.filter_by(
            uid = data['uid'],
        ).first()
        conversation.name = data['name']
        db.session.commit()
        return json_response(200, 'ok')
    except Exception as e:
        return json_response(500, f'error: {e}')
    

@bp.route('/save_conversation_messages', methods=['POST'], endpoint='save_conversation_messages')
def conversation_save_messages():
    try:
        data = request.get_json()
        conversation = Conversation.query.filter_by(uid=data['uid']).first()
        conversation.messages = data['messages']
        db.session.commit()
        return json_response(200, 'ok')
    except Exception as e:
        return json_response(500, f'error: {e}')
    

@bp.route('/get_conversation_messages', methods=['POST'], endpoint='get_conversation_messages')
def conversation_get_messages():
    try:
        data = request.get_json()
        conversation = Conversation.query.filter_by(uid=data['uid']).first()
        return json_response(200, 'ok', {'messages': conversation.messages})
    except Exception as e:
        return json_response(500, f'error: {e}')