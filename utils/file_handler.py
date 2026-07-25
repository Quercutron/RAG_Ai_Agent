"""
文件处理工具
主要是文档加载器
"""
import hashlib
import os

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
from utils.logger_handler import logger

def get_file_md5_hex(file_path:str):
    """
    获取文件md5的十六进制字符串
    :return:
    """
    if not os.path.exists(file_path):
        logger.error(f"[md5计算]文件不存在：{file_path}")
        return None

    md5_obj= hashlib.md5()
    #分片读取
    chunk_size = 4096
    try:
        with open(file_path, 'rb') as f:
            """
            chunk= f.read(chunk_size)
            while chunk:
                md5_obj.update(chunk)
                chunk= f.read(chunk_size)
            """
            while chunk:= f.read(chunk_size):
                md5_obj.update(chunk)

            #获取md5的十六进制字符串
            md5_hex= md5_obj.hexdigest()
            return md5_hex
    except Exception as e:
            logger.error(f"[md5计算]文件读取失败：{file_path}，错误信息：{e}")


def listdir_with_allow_type(path:str, allow_types:tuple[str]):
    """
    列出指定目录下的文件(允许的文件后缀)，并过滤掉不允许的文件类型
    :return:返回可操作的文件路径
    """
    files=[]
    #判断是否是文件夹
    if not os.path.isdir(path):
        logger.error(f"[文件列表]路径不是文件夹：{path}")
        return []

    #按列读取文件夹对象
    for f in os.listdir(path):
        #如果对象结尾符合类型，就将文件路径返回
        if f.endswith(allow_types):
            files.append(os.path.join(path, f))

    return files

def pdf_loader(file_path:str,password:str=None)->list[Document]:
    """
    pdf文件加载器
    :param file_path:文件路径
    :param password: 密码
    :return:Document对象列表
    """
    return PyPDFLoader(file_path,password=password).load()

def text_loader(file_path:str)->list[Document]:
    """
    文本文件加载器
    :param file_path:文件路径
    :return: Document对象列表
    """
    return TextLoader(file_path,encoding="utf-8").load()

