# commands/dataset_init_milvus.py
import click
from pymilvus import connections
from apps.dataset.milvus_models import DatasetMilvusModel

@click.command("dataset_init_milvus")
def run():

    # 检查连接状态
    if connections.has_connection("default"):
        print("Successfully connected to Milvus")
    else:
        print("Failed to connect to Milvus")

    # 删除集合
    DatasetMilvusModel.drop_collection()

    # 初始化集合并创建索引
    DatasetMilvusModel.init_collection()
    DatasetMilvusModel.create_index()

    click.echo("[command] init_milvus success.")