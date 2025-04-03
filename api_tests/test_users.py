import pytest
import allure
import requests
from core.api_client import api_client # 导入封装好的 client
from common.logger import logger

# 使用 Allure 来更好地组织报告
@allure.feature("User Management") # 功能模块
class TestUsers:

    @allure.story("Get User List") # 用户故事或场景
    @allure.title("Test getting a list of users (page 2)") # 测试用例标题
    @allure.description("Verify that we can successfully retrieve the second page of the user list.") # 详细描述
    @pytest.mark.api # 标记为 API 测试
    @pytest.mark.smoke # 可以标记为 Smoke 测试
    def test_list_users_page_2(self):
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
    def test_get_single_user_found(self):
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
    def test_get_single_user_not_found(self):
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