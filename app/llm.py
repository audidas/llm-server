from typing import List

from requests import post

from requests import get


from app.config import LLMConfig


def stream_message(conversation_id, context):
    response = post(
        f"http://10.0.30.198:12009/knowledge/chat/{conversation_id}",
        json=context,
        stream=True,
    )
    return response


# def knowledge_prompt(context: List[dict]):
#     return post(url=f"http://10.0.30.198:12009/knowledge/prompt", json=context).json()


def map_message(context: List[dict]):
    response = post(url="http://10.0.10.102:12002/map/chat", json=context)
    return response.json()
