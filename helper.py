# helper.py
import json
from openai import OpenAI, AzureOpenAI
from config import *


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def segment_text(text, segment_length=500, overlap=100):
    """
    根据指定的段落长度和重叠长度，将文本分段
    """
    segments = []
    start = 0
    while start < len(text):
        end = start + segment_length
        segments.append(text[start:end])
        start += segment_length - overlap
    return segments



#################Azure OpenAI#################


def get_embedding_model():
    return EMBEDDING_MODELS[EMBEDDING_MODEL_NAME]

def get_llm_embedding(input):
    model = get_embedding_model()
    
    # 创建 Azure OpenAI 客户端
    client = AzureOpenAI(
        azure_endpoint=model['endpoint'],
        api_key=model['api_key'],
        api_version=model['api_version']
    )
    
    try:
        response = client.embeddings.create(
            input=input,
            model=model['deployment_name'],  # 使用部署名称
            encoding_format="float"
        )
        return response
    except Exception as e:
        print(f"Error creating embedding: {str(e)}")
        raise


# def get_llm_chat(messages, model_name='azure', stream=False):
#     model = LLM_MODELS[model_name]
#     client = AzureOpenAI(
#         azure_endpoint=model['endpoint'],
#         api_key=model['api_key'],
#         api_version=model['api_version']
#     )
#     response = client.chat.completions.create(
#         model=model['deployment_name'],  # Azure 使用 deployment_name
#         messages=messages,
#         temperature=0.7,
#         stream=stream
#     )
#     return response

def get_llm_chat(messages, model_name, stream=False):
    model = LLM_MODELS[model_name]
    
    # Azure OpenAI
    if model_name.startswith('azure'):
        client = AzureOpenAI(
            azure_endpoint=model['endpoint'],
            api_key=model['api_key'],
            api_version=model['api_version']
        )
        response = client.chat.completions.create(
            model=model['deployment_name'],
            messages=messages,
            temperature=0.1,
            stream=stream
        )
    # 通义千问（包括本地部署和云端）
    else:
        client = OpenAI(
            base_url=model['base_url'],
            api_key=model['api_key']
        )
        response = client.chat.completions.create(
            model=model['model_name'],
            messages=messages,
            temperature=0.1,
            stream=stream
        )
    
    return response

# 测试代码
# if __name__ == "__main__":
#     try:
#         print("Testing embedding...")
#         print(f"Using deployment: {EMBEDDING_MODELS[EMBEDDING_MODEL_NAME]['deployment_name']}")
#         response = get_llm_embedding("Hello, world!")
#         print("Success!")
#         print(f"Embedding dimensions: {len(response.data[0].embedding)}")
#     except Exception as e:
#         print(f"Test failed: {str(e)}")




def json_response(status, message, data=None, errors=None):
    response = {
        'status': status,
        'message': message
    }
    if data is not None:
        response['data'] = data
    if errors is not None:
        response['errors'] = errors
    return json.dumps(response)


if __name__ == '__main__':
    resp = get_llm_chat([
        {'role': 'user', 'content': '给我讲个笑话.'}
    ], 'azure')  # 使用 'azure' 作为 model_name，因为这是我们在 LLM_MODELS 中定义的键
    
    # 更好的错误处理和输出
    try:
        print("Response:", resp)
        print("\nContent:", resp.choices[0].message.content)
    except Exception as e:
        print(f"Error occurred: {str(e)}")