"""
提示词加载工具
系统提示词
rag提示词
报告提示词
"""
from utils.config_handler import prompts_conf
from utils.path_tool import get_abs_path
from utils.logger_handler import logger

def load_system_prompt():
    try:
        system_prompt_path=get_abs_path(prompts_conf["main_prompts_path"])
    except KeyError as e:
        logger.error(f"[load_system_prompt]加载system系统提示词失败，请检查配置文件rag.yml，错误信息：{e}")
        raise e

    try:
        return open(system_prompt_path,"r",encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_system_prompt]解析system系统提示词出错，错误信息：{str(e)}]")
        raise e

def load_rag_prompt():
    try:
        rag_prompt_path=get_abs_path(prompts_conf["rag_summarize_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_rag_prompt]加载rag提示词失败，请检查配置文件rag.yml，错误信息：{e}")
        raise e

    try:
        return open(rag_prompt_path,"r",encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_rag_prompt]解析系统提示词出错，错误信息：{str(e)}]")
        raise e

def load_report_prompt():
    try:
        report_prompt_path=get_abs_path(prompts_conf["report_prompt_path"])
    except KeyError as e:
        logger.error(f"[report_prompt_path]加载report提示词失败，请检查配置文件rag.yml，错误信息：{e}")
        raise e

    try:
        return open(report_prompt_path,"r",encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[report_prompt_path]解析report提示词出错，错误信息：{str(e)}]")
        raise e

if __name__=="__main__":
    print(load_report_prompt())






















