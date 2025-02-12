# commands/test_milvus.py
import click
from random import random
from pymilvus import connections
from apps.dataset.milvus_models import DatasetMilvusModel

@click.command("test_milvus")
def run():
    # 检查连接状态
    if connections.has_connection("default"):
        print("Successfully connected to Milvus")
    else:
        print("Failed to connect to Milvus")
    
    # 初始化集合并创建索引(仅首次使用)
    # DatasetMilvusModel.init_collection()
    # DatasetMilvusModel.create_index()

    # 插入数据(示例)
    # data = [
    #     {"dataset_id": 1, "document_id": 1, "segment_id": 1, "text_vector": [random() for i in range(1536)]},
    #     {"dataset_id": 1, "document_id": 1, "segment_id": 2, "text_vector": [random() for i in range(1536)]},
    #     {"dataset_id": 2, "document_id": 2, "segment_id": 1, "text_vector": [random() for i in range(1536)]},
    #     {"dataset_id": 2, "document_id": 2, "segment_id": 2, "text_vector": [random() for i in range(1536)]},
    #     {"dataset_id": 2, "document_id": 2, "segment_id": 3, "text_vector": [random() for i in range(1536)]},
    # ]
    # DatasetMilvusModel.insert(data)

    # 查询数据
    # records = DatasetMilvusModel.query('dataset_id==1')
    # print(records)
    # print(len(records))

    # # 查看数据数量
    # print(DatasetMilvusModel.get_entity_count())
    
    
    # 删除数据
    # delete_expr = 'segment_id==3 and dataset_id==2'
    # DatasetMilvusModel.delete(delete_expr)

    # # 删除集合(一般不用)
    # DatasetMilvusModel.drop_collection()

    ## 向量检索
    query_vector_test = [random() for i in range(1536)]
    records = DatasetMilvusModel.search([query_vector_test], 3)
    # records = DatasetMilvusModel.search([[random() for i in range(1536)]], 3)
    for record in records[0]:
        print(record)