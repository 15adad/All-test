import logging

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from assistant.app.config import settings

logging = logging.getLogger(__name__)

from functools import lru_cache


# 将函数返回值缓存起来，下次直接从缓存中取Chroma对象不用每次都在磁盘中加载
@lru_cache(maxsize=1)
def _get_vectorstore():
    return Chroma(
        persist_directory=settings.PERSISTENT_DIRECTORY,
        embedding_function=OllamaEmbeddings(model=settings.LLM_EMBEDDING_MODEL),
        collection_name=settings.COLLECTION_NAME
    )
