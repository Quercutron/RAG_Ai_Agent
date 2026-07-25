"""
总结服务：用户提问，搜索参考资料，将提问和参考资料提交给模型，让模型总结回复
"""
from utils.config_handler import chroma_conf
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model
from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompt


class RagSummarizeService(object):
    def __init__(self):
        self.vector_service = VectorStoreService()
        self.prompt_text = load_rag_prompt()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self.__init__chain()
        # 从配置读取截断参数
        self.max_chunk_chars = chroma_conf.get("max_chunk_chars", 150)
        self.max_context_chars = chroma_conf.get("max_context_chars", 500)

    def __init__chain(self):
        chain = self.prompt_template | self.model | StrOutputParser()
        return chain

    def retriever_docs(self, query: str):
        """带相似度阈值过滤的检索"""
        return self.vector_service.search_with_threshold(query)

    def rag_summarize(self, query: str):
        context_docs = self.retriever_docs(query)

        # ① 逐个chunk截断 + ② 总长度限制
        context_chunks = []
        total_chars = 0
        for doc in context_docs:
            chunk_text = doc.page_content[:self.max_chunk_chars]
            overhead = len("【参考资料：】\n")
            if total_chars + len(chunk_text) + overhead > self.max_context_chars:
                break
            context_chunks.append(chunk_text)
            total_chars += len(chunk_text) + overhead

        context = ""
        for chunk_text in context_chunks:
            context += f"【参考资料：{chunk_text}】\n"

        return self.chain.invoke({"input": query, "context": context})


if __name__ == "__main__":
    service = RagSummarizeService()
    print(service.rag_summarize("小户型适合什么扫地机器人"))








