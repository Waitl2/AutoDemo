# common/assertions.py
import pytest
import allure
from common.logger import logger
import requests # requests.Response 类型提示



def assert_status_code(response: requests.Response, expected_code: int):
    """
    断言响应的状态码是否符合预期。

    :param response: requests 返回的 Response 对象
    :param expected_code: 预期的 HTTP 状态码
    """
    step_desc = f"Verify response status code is {expected_code}"
    logger.info(step_desc)
    with allure.step(step_desc):
        actual_code = response.status_code
        assert actual_code == expected_code, \
            f"Assertion Failed: Expected status code {expected_code}, but got {actual_code}. " \
            f"URL: {response.request.url}, Response: {response.text[:500]}..." # 限制响应文本长度

def assert_json_value(response: requests.Response, json_path: str, expected_value):
    """
    断言响应体 JSON 中指定路径 (支持点号'.'分隔) 的值是否符合预期。

    :param response: requests 返回的 Response 对象
    :param json_path: JSON 路径字符串 (e.g., 'page', 'data.id', 'data.0.email' for lists - see note)
                      NOTE: Simple list index access like 'data.0.email' is added.
                      For more complex queries, consider libraries like jsonpath-ng.
    :param expected_value: 预期的值
    """
    step_desc = f"Verify JSON value at path '{json_path}' is '{expected_value}'"
    logger.info(step_desc)
    with allure.step(step_desc):
        try:
            response_json = response.json()
            logger.debug(f"Asserting on JSON: {response_json}")
            keys = json_path.split('.')
            actual_value = response_json
            current_path_str = "root"

            for key in keys:
                logger.debug(f"Navigating: current path='{current_path_str}', next key='{key}', current value type='{type(actual_value)}'")
                if isinstance(actual_value, dict):
                    if key in actual_value:
                        actual_value = actual_value[key]
                        current_path_str += f".{key}"
                    else:
                        pytest.fail(f"Assertion Failed: Key '{key}' not found at path '{current_path_str}' in JSON. "
                                    f"Available keys: {list(actual_value.keys())}. Full JSON: {response_json}")
                elif isinstance(actual_value, list):
                    try:
                        # Try interpreting the key as an integer index for lists
                        index = int(key)
                        if 0 <= index < len(actual_value):
                            actual_value = actual_value[index]
                            current_path_str += f".[{index}]" # Indicate list access in path
                        else:
                             pytest.fail(f"Assertion Failed: Index {index} out of bounds for list at path '{current_path_str}'. "
                                         f"List size: {len(actual_value)}. Full JSON: {response_json}")
                    except ValueError:
                        # Key is not a valid integer index for the list
                        pytest.fail(f"Assertion Failed: Key '{key}' is not a valid integer index for list at path '{current_path_str}'. "
                                    f"Full JSON: {response_json}")
                else:
                    # We are trying to access a key/index on something that's not a dict or list
                    pytest.fail(f"Assertion Failed: Cannot access key/index '{key}' on non-dict/non-list element "
                                f"(type: {type(actual_value)}) at path '{current_path_str}'. Full JSON: {response_json}")

            # After loop, actual_value holds the final navigated value
            logger.debug(f"Final navigated value at path '{json_path}': {actual_value} (type: {type(actual_value)})")
            assert actual_value == expected_value, \
                f"Assertion Failed: Expected JSON value '{expected_value}' (type: {type(expected_value)}) at path '{json_path}', " \
                f"but got '{actual_value}' (type: {type(actual_value)}). Full JSON: {response_json}"

        except requests.exceptions.JSONDecodeError:
            logger.error(f"Failed to decode JSON response. Response text: {response.text}")
            pytest.fail(f"Cannot assert JSON value: Response is not valid JSON. URL: {response.request.url}")
        except Exception as e: # Catch other potential errors during navigation/assertion
             logger.exception(f"An unexpected error occurred during JSON value assertion for path '{json_path}': {e}")
             pytest.fail(f"Unexpected error during assertion for path '{json_path}': {e}. "
                         f"Response Text: {response.text[:500]}...")


# --- Keep assert_json_keys_exist and assert_payload_in_response as they are ---
# They operate on the top-level JSON or specific dictionaries.
def assert_json_keys_exist(response: requests.Response, keys: list):
    """
    断言响应体 JSON 中是否包含所有指定的键。

    :param response: requests 返回的 Response 对象
    :param keys: 预期必须存在的键列表 (list of strings)
    """
    step_desc = f"Verify JSON contains keys: {keys}"
    logger.info(step_desc)
    with allure.step(step_desc):
        try:
            response_json = response.json()
            missing_keys = [key for key in keys if key not in response_json]
            assert not missing_keys, \
                f"Assertion Failed: Missing expected JSON keys: {missing_keys}. " \
                f"Available keys: {list(response_json.keys())}"
        except requests.exceptions.JSONDecodeError:
            logger.error(f"Failed to decode JSON response. Response text: {response.text}")
            pytest.fail(f"Cannot assert JSON keys: Response is not valid JSON. URL: {response.request.url}")
        except AttributeError:
            pytest.fail(f"Cannot assert JSON keys: Response JSON is not a dictionary or None. URL: {response.request.url}")
    pass


def assert_payload_in_response(response: requests.Response, payload: dict):
    """
    断言请求的 payload 中的键值对是否都存在于响应体 JSON 中。

    :param response: requests 返回的 Response 对象
    :param payload: 发送请求时使用的 payload 字典
    """
    step_desc = f"Verify request payload values are reflected in response: {list(payload.keys())}"
    logger.info(step_desc)
    with allure.step(step_desc):
        try:
            response_json = response.json()
            mismatches = {}
            for key, expected_value in payload.items():
                actual_value = response_json.get(key)
                if actual_value != expected_value:
                    mismatches[key] = {'expected': expected_value, 'actual': actual_value}

            assert not mismatches, \
                f"Assertion Failed: Payload values mismatch in response. Mismatches: {mismatches}. " \
                f"Full JSON: {response_json}"
        except requests.exceptions.JSONDecodeError:
            logger.error(f"Failed to decode JSON response. Response text: {response.text}")
            pytest.fail(f"Cannot assert payload in response: Response is not valid JSON. URL: {response.request.url}")
        except AttributeError:
            pytest.fail(f"Cannot assert payload in response: Response JSON is not a dictionary or None. URL: {response.request.url}")
    pass

# 可以在这里添加更多断言函数，例如：
# - assert_json_schema(response, schema) # 使用 jsonschema 库进行模式校验
# - assert_response_time(response, max_time_ms)
# - assert_header_value(response, header_name, expected_value)
# - assert_error_message_contains(response, expected_message) # 用于失败场景