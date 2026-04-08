from langchain_openai import ChatOpenAI
from config.settings import settings


def get_chat_model(temperature=0.7, structured_output_schema=None, streaming=False):
    """
    获取一个标准的聊天模型实例
    """
    llm = ChatOpenAI(
        model=settings.LLM_MODEL_NAME,
        openai_api_key=settings.LLM_API_KEY,
        openai_api_base=settings.LLM_BASE_URL,
        temperature=temperature,
        max_retries=3,  # 统一设置重试
        # model_kwargs={"seed": 42} # 统一设置随机种子保证一致性,
        streaming=streaming,
    )
    
    # 如果需要结构化输出，直接在这里绑定
    if structured_output_schema:
        return llm.with_structured_output(structured_output_schema)
    
    return llm
