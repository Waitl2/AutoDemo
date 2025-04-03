import yaml
import os

def get_config(config_path = None):
    
    """
    读取配置文件
    ：param config_path: 配置文件路径，默认值为 None，表示读取当前目录下的 config.yaml 文件
    :return: 返回配置字典
    """
    if config_path is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config','config.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        print(f"配置文件未找到: {config_path}")
        return None
    except yaml.YAMLError as e:
        print(f"读取配置文件时发生错误: {e}")
        return None
    
# config = get_config()

# 示例：如何获取配置项
# if __name__ == '__main__':
#     if config:
#         print("API Base URL:", config.get('api', {}).get('base_url'))
#         print("Web Browser:", config.get('web', {}).get('browser'))
#         print("Logging Level:", config.get('logging', {}).get('level'))