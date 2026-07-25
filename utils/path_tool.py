"""
为整个工程提供统一的绝对路径
"""
import os.path


def get_project_root()->str:
    """
    获取当前工程根目录的绝对路径
    :return: 字符串根目录
    """
    current_file=os.path.abspath(__file__)
    current_dir=os.path.dirname(current_file)

    return os.path.dirname(current_dir)

def get_abs_path(relative_path:str)->str:
    """
    获取当前工程根目录下某个相对路径的绝对路径
    :param relative_path: 相对路径
    :return: 字符串绝对路径
    """
    project_root=get_project_root()
    return os.path.join(project_root,relative_path)