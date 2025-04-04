# conftest.py
import pytest
from core.api_client import ApiClient  # 导入我们定义的ApiClient类
from common.logger import logger          # 导入日志记录器

@pytest.fixture(scope="session") # 使用 session 作用域，保证整个测试运行期间只创建一个实例
def api_client():
    """
    提供一个 session 级别的 ApiClient 实例。
    """
    logger.info("--- Initializing API Client Fixture (Session Scope) ---")
    client = ApiClient()
    # 如果未来需要进行全局的 setup，例如获取认证 token，可以在这里添加
    # client.authenticate(...)
    yield client  # yield 将 client 实例提供给测试函数
    # yield 之后的部分是 teardown 代码
    logger.info("--- Tearing down API Client Fixture (Session Scope) ---")
    # 如果有全局的清理操作，例如退出登录，可以在这里添加
    # client.logout(...)

# 你可以在这里添加其他全局的 fixtures，例如数据库连接、Web Driver 等。