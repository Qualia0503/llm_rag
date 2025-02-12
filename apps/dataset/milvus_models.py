# apps/dataset/milvus_models.py
from extensions.ext_milvus import MilvusBaseModel
from pymilvus import FieldSchema, CollectionSchema, DataType
from helper import get_embedding_model

embedding_model = get_embedding_model()
vector_dim = embedding_model['vector_dim']

class DatasetMilvusModel(MilvusBaseModel):
    collection_name = "dataset_collection"
    schema = CollectionSchema(
        fields=[
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="dataset_id", dtype=DataType.INT64),
            FieldSchema(name="document_id", dtype=DataType.INT64),
            FieldSchema(name="segment_id", dtype=DataType.INT64),
            FieldSchema(name="text_vector", dtype=DataType.FLOAT_VECTOR, dim=vector_dim),
        ],
        description="A collection for storing datasets",
    )
    index_params = {
        "index_type": "IVF_FLAT",
        "metric_type": "L2",
        "params": {"nlist": vector_dim},
    }
    index_field_name = "text_vector"