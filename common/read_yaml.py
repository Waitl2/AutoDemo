# common/read_yaml.py
import yaml
import os
from common.logger import logger

def read_yaml(file_path):
    """
    读取 YAML 文件并返回其内容。
    :param file_path:相对于项目根目录的 YAML 文件路径 (e.g., 'data/user_creation_data.yaml')
    :return: 解析后的 Python 对象 (通常是列表或字典)，如果失败则返回 None
    """
        # 构建绝对路径
    try: # Add a try block for safety during debugging
        # <<<--- Add debug prints here --->>>
        current_file_abspath = os.path.abspath(__file__)
        common_dir = os.path.dirname(current_file_abspath)
        project_root = os.path.dirname(common_dir)

        print(f"DEBUG: Type of project_root: {type(project_root)}, Value: {project_root}")
        print(f"DEBUG: Type of file_path: {type(file_path)}, Value: {file_path}")
        # <<<---------------------------->>>

        full_path = os.path.join(project_root, file_path) # Error occurs here

        logger.debug(f"Attempting to read YAML file: {full_path}")
        # ... (rest of the function: open, load, return) ...
    except Exception as e:
        logger.error(f"An error occurred during path calculation or reading {file_path}: {e}")
        print(f"ERROR during read_yaml execution: {e}") # Also print to console
        return None # Ensure None is returned on error
    # 构建绝对路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(project_root, file_path)

    logger.debug(f"Attempting to read YAML file: {full_path}")
    try:
        with open(full_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            logger.debug(f"Successfully read and parsed YAML data from {full_path}")
            return data
    except FileNotFoundError:
        logger.error(f"Error: YAML file not found at {full_path}")
        return None
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file {full_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while reading {full_path}: {e}")
        return None

# # 示例用法
# if __name__ == '__main__':
#     user_data = read_yaml('data/user_creation_data.yaml')
#     if user_data:
#         print(user_data)
#
#     non_existent_data = read_yaml('data/non_existent.yaml')
#     print(non_existent_data) # Should print None and log an error