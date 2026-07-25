"""
模型工厂
"""
import os
from abc import ABC, abstractmethod
from typing import Optional
from dotenv import load_dotenv
from langchain_community.embeddings import DashScopeEmbeddings

from utils.config_handler import rag_conf
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI


load_dotenv()


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass


class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return ChatOpenAI(
            model=rag_conf["chat_model_name"],
            api_key=os.getenv("QWEN_API_KEY"),
            base_url=os.getenv("QWEN_BASE_URL"),
            request_timeout=rag_conf.get("request_timeout", 120),
            max_retries=rag_conf.get("max_retries", 2),
        )


class EmbeddingModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return DashScopeEmbeddings(
            model=rag_conf["embedding_model_name"],
            dashscope_api_key=os.getenv("QWEN_API_KEY"),
        )


# 创建模型实例对象
# generator:生成器
chat_model = ChatModelFactory().generator()
embedding_model = EmbeddingModelFactory().generator()
