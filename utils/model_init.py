from langchain.chat_models import init_chat_model
from langchain_core.callbacks import CallbackManager
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain_community.chat_models import ChatTongyi
qwen3_vl = init_chat_model(
    base_url="http://10.16.6.16:11434/",
    model="qwen3-vl-local",
    model_provider="ollama",
    temperature=0.1,
    max_tokens=2048,
    timeout=120,  # 多模态推理耗时更长，延长超时
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)
qwen3 = ChatTongyi(
    model="qwen-plus-2025-07-28",
    api_key="sk-f1c8b422da5d4582b78a5ad5e0e7557b",
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)
