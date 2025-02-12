from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",

    api_key="ollama"
)

chat_completion = client.chat.completions.create(
    messages=[
        {
        "role": "user", 
        "content": "写一个Python装饰器的示例"},
        stream=True,
    ],
    model = "deepseek-r1")

print(chat_completion.choices[0].message.content)