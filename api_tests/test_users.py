import pytest
import allure
import requests
# from core.api_client import api_client # 导入封装好的 client
from common.logger import logger
from common.read_yaml import read_yaml

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
        logger.info("Starting test: test_list_users_page_2")
        endpoint = "/users"
        params = {'page': 2}

        # 发送 GET 请求
        response = api_client.get(endpoint, params=params)

        # --- 断言 ---
        # 1. 状态码断言
        with allure.step("Verify response status code is 200"): # Allure 报告中的步骤
            logger.info(f"Asserting status code: expected=200, actual={response.status_code}")
            assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

        # 2. 响应体基本结构断言 (根据 Reqres.in 的实际响应)
        response_json = response.json() # 解析 JSON 响应体
        logger.debug(f"Response JSON: {response_json}") # 记录响应体便于调试

        with allure.step("Verify response body structure and key fields"):
            logger.info("Asserting response body structure")
            assert 'page' in response_json, "Response JSON should contain 'page' key"
            assert 'per_page' in response_json, "Response JSON should contain 'per_page' key"
            assert 'total' in response_json, "Response JSON should contain 'total' key"
            assert 'total_pages' in response_json, "Response JSON should contain 'total_pages' key"
            assert 'data' in response_json, "Response JSON should contain 'data' key"
            assert isinstance(response_json['data'], list), "'data' should be a list"

        # 3. 响应体具体值断言 (根据 Reqres.in 的已知响应)
        with allure.step("Verify response data content"):
            logger.info("Asserting specific values in response")
            assert response_json['page'] == 2, f"Expected page 2, but got {response_json['page']}"
            # 可以添加更多断言，比如检查 data 列表不为空，或者第一个用户的 email 格式等
            if len(response_json['data']) > 0:
                first_user = response_json['data'][0]
                assert 'id' in first_user
                assert 'email' in first_user
                assert 'first_name' in first_user
                assert 'last_name' in first_user
                assert '@' in first_user['email'], "User email should contain '@'"
            else:
                logger.warning("User data list is empty, skipping detailed user checks.")

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

        with allure.step("Verify response status code is 200"):
            logger.info(f"Asserting status code: expected=200, actual={response.status_code}")
            assert response.status_code == 200

        response_json = response.json()
        logger.debug(f"Response JSON: {response_json}")

        with allure.step("Verify response contains user data"):
            logger.info("Asserting response body structure and user ID")
            assert 'data' in response_json, "Response JSON should contain 'data' key"
            user_data = response_json['data']
            assert isinstance(user_data, dict), "'data' should be a dictionary"
            assert user_data.get('id') == user_id, f"Expected user ID {user_id}, but got {user_data.get('id')}"
            assert 'email' in user_data
            assert 'first_name' in user_data
            assert 'last_name' in user_data

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

        with allure.step("Verify response status code is 404"):
            logger.info(f"Asserting status code: expected=404, actual={response.status_code}")
            assert response.status_code == 404, f"Expected status code 404 for non-existing user, but got {response.status_code}"

        # 对于 404，Reqres.in 通常返回一个空的响应体，可以断言这一点
        with allure.step("Verify response body is empty"):
            logger.info("Asserting response body is empty")
            # 检查响应体是否为空或者是否可以解析为空字典
            try:
                assert response.json() == {}, "Expected empty JSON object for 404 response"
            except requests.exceptions.JSONDecodeError:
                # 如果响应体为空文本，json() 会抛出异常，这也是可接受的
                 assert response.text == '{}' or response.text == '', "Expected empty body for 404 response"


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

        # --- 断言 ---
        # 1. 状态码断言
        with allure.step(f"Verify response status code is {expected_status}"):
            logger.info(f"Asserting status code: expected={expected_status}, actual={response.status_code}")
            assert response.status_code == expected_status, \
                   f"Expected status code {expected_status}, but got {response.status_code}. Response: {response.text}"

        # 2. 响应体断言 (根据预期是成功还是失败)
        response_json = {}
        response_text = response.text
        if response.content: # 检查是否有响应体
             try:
                 response_json = response.json()
                 logger.debug(f"Response JSON: {response_json}")
             except Exception as e:
                 logger.warning(f"Could not decode JSON response: {e}. Response text: {response_text}")

        if expected_status // 100 == 2: # 如果预期是成功 (2xx)
             with allure.step("Verify successful response body content and structure"):
                 logger.info("Asserting successful response body")
                 # 断言 payload 中的字段是否在响应中存在且值匹配
                 for key, value in payload.items():
                      assert response_json.get(key) == value, \
                             f"Payload key '{key}' mismatch: expected '{value}', got '{response_json.get(key)}'"
                 # 断言预期必须存在的 key
                 if expected_keys:
                     for key in expected_keys:
                         assert key in response_json, f"Expected key '{key}' not found in response keys: {list(response_json.keys())}"
                 # 可以添加其他更具体的成功断言
                 logger.info(f"User '{payload.get('name')}' seems to be created successfully. ID: {response_json.get('id')}")

        else: # 如果预期是失败 (非 2xx)
             with allure.step("Verify error response body (if applicable)"):
                 logger.info("Asserting error response body")
                 if expected_error:
                      # 断言预期的错误信息是否存在于响应体中 (需要根据实际 API 的错误格式调整)
                      # 这里假设错误信息在 'error' 字段或直接在响应文本中
                      error_found = False
                      if 'error' in response_json and expected_error in response_json['error']:
                          error_found = True
                      elif expected_error in response_text:
                           error_found = True

                      assert error_found, \
                             f"Expected error message '{expected_error}' not found in response: {response_text}"
                      logger.info(f"Verified expected error message: '{expected_error}'")
                 else:
                      logger.info("No specific error message assertion was defined for this failure case.")


        logger.info(f"Test '{description}' finished.")

