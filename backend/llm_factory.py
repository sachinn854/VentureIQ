from langchain_openai import ChatOpenAI
from backend.config import settings


def get_llm(max_tokens: int = 4096, max_retries: int = 3) -> ChatOpenAI:
    extra_body = {}
    if settings.openrouter_provider:
        extra_body['provider'] = {
            'order': [settings.openrouter_provider],
            'allow_fallbacks': True,
        }

    return ChatOpenAI(
        model=settings.model_name,
        api_key=settings.openrouter_api_key,
        base_url='https://openrouter.ai/api/v1',
        max_tokens=max_tokens,
        max_retries=max_retries,
        model_kwargs={'extra_body': extra_body} if extra_body else {},
    )
