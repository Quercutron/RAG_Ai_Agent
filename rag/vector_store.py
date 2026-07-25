import os.path
from utils.logger_handler import logger
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.config_handler import chroma_conf
from model.factory import embedding_model
from utils.path_tool import get_abs_path
from utils.file_handler import text_loader, pdf_loader, listdir_with_allow_type, get_file_md5_hex


class VectorStoreService(object):
    def __init__(self):
        # 初始化向量存储对象，使用Chroma库创建向量数据库
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],  # 设置集合名称
            embedding_function=embedding_model,              # 使用预定义的嵌入模型
            persist_directory=get_abs_path(chroma_conf["persist_directory"]),  # 统一使用项目根绝对路径
        )

        #文本分割器
        self.spliter= RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],
            chunk_overlap=chroma_conf["chunk_overlap"],
            separators=chroma_conf["separators"],
            length_function=len,
        )

    def get_retriever(self):
    # 定义一个获取检索器的方法
    # 返回一个基于向量存储的检索器对象
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_conf["k"]})

    def search_with_threshold(self, query: str) -> list[Document]:
        """带相似度阈值过滤的检索，仅返回低于阈值的chunk"""
        threshold = chroma_conf.get("similarity_threshold", 1.0)
        results = self.vector_store.similarity_search_with_score(
            query, k=chroma_conf["k"]
        )
        filtered = []
        for doc, score in results:
            if score <= threshold:
                logger.info(f"[检索]相似度score={score:.4f} <= 阈值{threshold}，保留")
                filtered.append(doc)
            else:
                logger.info(f"[检索]相似度score={score:.4f} > 阈值{threshold}，丢弃")
        return filtered

    def load_document(self):
        """
        加载知识库，从数据文件夹内读取数据文件，则转为向量存入向量数据库
        要计算文件的md5去重
        """
        #检查md5对象
        def check_md5_hex(md5_for_check:str):
            # 检查md5_hex文件是否存在
            # 如果在，则返回True，否则返回False
            md5_store_path = get_abs_path(chroma_conf["md5_hex_store"])
            if not os.path.exists(md5_store_path):
                open(md5_store_path, 'w',encoding='utf-8').close()
                return False

            # 检查md5_hex是否在向量数据库中
            with open(md5_store_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # 去掉换行符
                    if line.strip() == md5_for_check:
                        return True
                return False

        # 加载文件
        def save_md5_hex(md5_for_check:str):
            # 保存文件内容
            with open(get_abs_path(chroma_conf["md5_hex_store"]), 'a',encoding='utf-8') as f:
                f.write(md5_for_check + '\n')
        def get_file_document(read_path:str):
            if read_path.endswith('txt'):
                return text_loader(read_path)

            if read_path.endswith('pdf'):
                return pdf_loader(read_path)

            return []

        allowed_files_path:list[str]=listdir_with_allow_type(
            get_abs_path(chroma_conf["data_path"]),
            tuple(chroma_conf["allow_knowledge_file_type"])
        )

        for file_path in allowed_files_path:
            # 获取文件的md5值
            md5_hex = get_file_md5_hex(file_path)
            # 检查md5值是否在向量数据库中
            if check_md5_hex(md5_hex):
                logger.info(f"[加载知识库]文件内容已存在：{file_path}，跳过")
                continue

            # 如果不在，则将文件内容转为向量存入向量数据库
            try:
                #确定文件类型
                documents:list[Document] = get_file_document(file_path)
                if not documents:
                    logger.error(f"[加载知识库]文件有效内容为空：{file_path}")
                    continue

                # 将文件内容转为向量存入向量数据库
                #分割——添加
                split_document:list[Document]=self.spliter.split_documents(documents)

                if not split_document:
                    logger.error(f"[加载知识库]文件分割后内容为空：{file_path}")
                    continue

                self.vector_store.add_documents(split_document)
                # 保存md5值
                save_md5_hex(md5_hex)

            except Exception as e:
                #exc_info为True时，会记录详细的报错堆栈，如果为False，则只会记录报错信息本身
                logger.error(f"[加载知识库]文件加载失败：{file_path}，错误信息：{str(e)}",exc_info=True)
                continue

if __name__ == '__main__':
    vs=VectorStoreService()

    vs.load_document()

    retriever=vs.get_retriever()

    res=retriever.invoke("迷路")
    for r in res:
        print(r)
        print("=="*10)












