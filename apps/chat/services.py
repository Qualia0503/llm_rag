# apps/chat/services.py
from helper import get_llm_embedding
from apps.dataset.milvus_models import DatasetMilvusModel
from apps.dataset.models import Segment
from config import *

def retrieve_related_texts(messages, params):
    # 拼接最近的对话内容
    input_str = ''
    for message in messages[-3:]:  ####这里可以把历史对话消息改的更多
        input_str += f"{message['role']}: {message['content']}\n\n"
    # print(input_str)
    # exit()

    # 召回相似文本
    vector_resp = get_llm_embedding(input_str)
    query_vector = vector_resp.data[0].embedding
    expr = ' or '.join([f'dataset_id=={dataset_id}' for dataset_id in params['dataset_ids']])
    # print(expr)
    # exit()
    related_objs = DatasetMilvusModel.search([query_vector], TOP_K, expr, ['dataset_id', 'document_id', 'segment_id'])
    # print(related_objs)
    # exit()
     # 处理数据
    segment_ids = []
    for hits in related_objs:
        for hit in hits:
            for field_name in hit.fields:
                if field_name == 'segment_id':
                    segment_ids.append(hit.entity.get(field_name))

    # print(segment_ids)
    # exit()

    # 查询片段并拼接内容
    segments = Segment.query.filter(Segment.id.in_(segment_ids)).all()
    content = '请参考以下内容，回答用户问题：\n\n'
    for segment in segments:
        content += segment.content + '\n\n'

    # print(content)
    # exit()

    # 往 messages 中插入召回的内容
    new_message = {'role': 'system', 'content': content}
    last_message = messages.pop()
    messages.append(new_message)
    messages.append(last_message)
    return messages