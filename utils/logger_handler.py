"""
日志工具
"""
import logging
import os
from datetime import datetime

from utils.path_tool import get_abs_path

#日志保存的根目录
LOG_ROOT = get_abs_path('logs')

#确保日志的目录存在
os.makedirs(LOG_ROOT, exist_ok=True)


#日志配置
DEFAULT_LOG_FORMAT=logging.Formatter(
    #时间-名字-级别-文件名：具体位置-日志正文
    '%(asctime)s - %(name)s - %(levelname)s-%(filename)s:%(lineno)d - %(message)s'
)

#日志控制器
def get_logger(
        name:str="agent",
        console_level:int=logging.INFO,
        file_level:int=logging.DEBUG,
        log_file:str=None,
)->logging.Logger:
    #创建logger对象
    logger = logging.getLogger(name)

    #设置日志级别
    logger.setLevel(logging.DEBUG)

    #避免重复添加handlers
    if logger.handlers:
        return logger

    #控制台Handler
    console_handler = logging.StreamHandler()
    #设置日志级别
    console_handler.setLevel(console_level)
    #设置日志格式
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)

    #添加文件日志处理器
    logger.addHandler(console_handler)

    #文件Handler
    if not log_file:
        #日志存放路径
        log_file = os.path.join(LOG_ROOT, f'{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.log')

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(file_handler)

    return logger

#快捷获取日志
logger=get_logger()

if __name__=='__main__':
    logger.info("信息日志")
    logger.error("错误日志")
    logger.warning("警告日志")
    logger.debug("调试日志")
















