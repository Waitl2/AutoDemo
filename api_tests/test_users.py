import pytest
import allure
import requests
# from core.api_client import api_client # 导入封装好的 client
from common.logger import logger
from common.read_yaml import read_yaml
# --- 导入封装的断言函数 ---
from common.assertions import (
    assert_status_code,
    assert_json_value,
    assert_json_keys_exist,
    assert_payload_in_response
)

user_creation_data_path = 'data/user_creation_data.yaml'
logger.info(f"Loading test data from: {user_creation_data_path}")
# user_creation_test_data = read_yaml(user_creation_data_path)
_user_creation_test_data_list = read_yaml(user_creation_data_path) # Use a temporary variable

# --- Handle potential loading failure ---
if _user_creation_test_data_list is None:
    logger.error(f"FATAL: Failed to load test data from {user_creation_data_path}. Skipping dependent tests.")
    # Assign an empty list to prevent parametrize from crashing during collection
    # Pytest will report 0 tests collected for the parametrized function, indicating a problem.
    _user_creation_test_data_list = []
    # Alternatively, raise a specific exception to halt collection more explicitly:
    # raise pytest.UsageError(f"Failed to load test data from {user_creation_data_path}")

# --- 提取测试 ID (only if data loaded successfully) ---
if _user_creation_test_data_list: # Check if list is not empty
    test_ids = [data.get('test_id', f'data_index_{i}') for i, data in enumerate(_user_creation_test_data_list)]
else:
    test_ids = [] # Empty list if data loading failed

# 使用 Allure 来更好地组织报告
@allure.feature("User Management") # 功能模块
class TestUsers:

    @allure.story("Get User List") # 用户故事或场景
    @allure.title("Test getting a list of users (page 2)") # 测试用例标题
    @allure.description("Verify that we can successfully retrieve the second page of the user list.") # 详细描述
    @pytest.mark.api # 标记为 API 测试
    @pytest.mark.smoke # 可以标记为 Smoke 测试
    def test_list_users_page_2(self, api_client):
        """
        测试获取用户列表第二页的功能
        对应接口: GET /api/users?page=2
        """
        logger.info("Starting test: test_get_single_user_found")
        user_id = 2
        endpoint = f"/users/{user_id}"

        # 发送 GET 请求
        response = api_client.get(endpoint)

        # --- 使用封装断言 ---
        assert_status_code(response, 200)
        assert_json_keys_exist(response, ['data']) 

        # Use the enhanced assertion function with dot notation
        assert_json_value(response, 'data.id', user_id)
        assert_json_value(response, 'data.email', 'janet.weaver@reqres.in') # Example of asserting another nested value
        assert_json_value(response, 'data.first_name', 'Janet')

        # If you wanted to assert keys within 'data', you might need a helper or assert them individually
        # Option: Assert individual keys exist within 'data'
        assert_json_value(response, 'data.last_name', 'Weaver') # Implicitly checks existence too
        # Or, create a helper assert_json_path_keys_exist(response, 'data', ['email', 'first_name', ...]) if needed often
        logger.info("Test test_list_users_page_2 finished successfully.")

    @allure.story("Get Single User")
    @allure.title("Test getting a single existing user (ID 2)")
    @pytest.mark.api
    def test_get_single_user_found(self, api_client):
        """
        测试获取单个存在用户的功能
        对应接口: GET /api/users/2
        """
        logger.info("Starting test: test_get_single_user_found")
        user_id = 2
        endpoint = f"/users/{user_id}"

        response = api_client.get(endpoint)

        # --- 使用封装断言 ---
        assert_status_code(response, 200)
        assert_json_keys_exist(response, ['data'])
         # Use the enhanced assertion function with dot notation
        assert_json_value(response, 'data.id', user_id)
        assert_json_value(response, 'data.email', 'janet.weaver@reqres.in') # Example of asserting another nested value
        assert_json_value(response, 'data.first_name', 'Janet')

        # If you wanted to assert keys within 'data', you might need a helper or assert them individually
        # Option: Assert individual keys exist within 'data'
        assert_json_value(response, 'data.last_name', 'Weaver') # Implicitly checks existence too
        # Or, create a helper assert_json_path_keys_exist(response, 'data', ['email', 'first_name', ...]) if needed often
        logger.info("Test test_get_single_user_found finished successfully.")


    @allure.story("Get Single User")
    @allure.title("Test getting a single non-existing user (ID 23)")
    @pytest.mark.api
    def test_get_single_user_not_found(self, api_client):
        """
        测试获取单个不存在用户的功能 (预期 404)
        对应接口: GET /api/users/23
        """
        logger.info("Starting test: test_get_single_user_not_found")
        user_id = 23 # Reqres.in 对于不存在的用户返回 404
        endpoint = f"/users/{user_id}"

        response = api_client.get(endpoint)

        assert_status_code(response, 404) # 断言状态码为 404
        # 断言响应体中包含预期的错误信息
        with allure.step("Verify response body is empty JSON object"):
             assert response.text == '{}' or response.text == '', \
                   f"Expected empty body or '{{}}' for 404, got: {response.text}"

        logger.info("Test test_get_single_user_not_found finished successfully.")
        
    #数据驱动创建用户测试
    @allure.story("Create User（数据驱动）")
    @allure.title("Test creating a user with data from YAML file")
    @pytest.mark.api
    @pytest.mark.regression # 可以标记为回归测试
    @pytest.mark.parametrize("test_data", _user_creation_test_data_list, ids=test_ids) # 使用 parametrize 进行数据驱动测试
    def  test_create_user_data_driven(self, api_client, test_data): # <--- 接收 test_data 参数
        """
        数据驱动测试创建新用户的功能
        对应接口: POST /api/users
        """
        # 从 test_data 中提取信息
        payload = test_data.get('payload', {})
        expected_status = test_data.get('expected_status')
        expected_keys = test_data.get('expected_keys')
        expected_error = test_data.get('expected_error_msg')
        description = test_data.get('description', 'No description')

        # 在 Allure 报告和日志中包含描述信息
        logger.info(f"Starting test: {description}")
        logger.debug(f"Test Data: {test_data}")
        allure.dynamic.description(f"Test Scenario: {description}<br>Payload: {payload}") # 动态设置描述

        endpoint = "/users"

        # 发送 POST 请求
        with allure.step(f"Send POST request to {endpoint} with payload: {payload}"):
            response = api_client.post(endpoint, json=payload)

        # --- 使用封装断言 ---
        assert_status_code(response, expected_status)

        if expected_status // 100 == 2: # 成功场景
             # 断言请求的 payload 是否反映在响应中
             assert_payload_in_response(response, payload)
             # 断言其他必须存在的 key
             if expected_keys:
                 assert_json_keys_exist(response, expected_keys)
             logger.info(f"User '{payload.get('name')}' creation seems successful.")
        else: # 失败场景
             # (需要添加处理失败场景的断言函数, e.g., assert_error_message_contains)
             if expected_error:
                 with allure.step(f"Verify error message contains '{expected_error}'"):
                      logger.info(f"Asserting error message contains: {expected_error}")
                      # 简单的实现：直接检查文本
                      assert expected_error in response.text, \
                             f"Expected error '{expected_error}' not found in response: {response.text}"
             else:
                 logger.info("No specific error message assertion defined for this failure case.")

        logger.info(f"Test '{description}' finished.")