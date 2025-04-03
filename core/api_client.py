import requests
from common.read_config import get_config
from common.logger import logger # 导入我们配置好的 logger

class ApiClient:
    def __init__(self):
        config = get_config() # <--- 在初始化时调用 get_config()
        if not config:
             logger.error("Failed to load configuration for ApiClient.")
             # 根据需要处理，可以抛出异常阻止实例化
             raise ValueError("API configuration could not be loaded.")

        self.base_url = config.get("api", {}).get("base_url")
        self.default_headers = config.get('api', {}).get('headers', {})
        self.default_timeout = config.get('api', {}).get('timeout', 10)
        logger.info(f"API Client initialized with base URL: {self.base_url}")

    def _send_request(self, method, endpoint, **kwargs):
        """内部方法，用于发送所有类型的请求"""
        url = f"{self.base_url}{endpoint}"
        headers = {**self.default_headers, **kwargs.pop('headers', {})} # 合并默认和自定义 headers
        timeout = kwargs.pop('timeout', self.default_timeout)

        logger.debug(f"Sending {method.upper()} request to: {url}")
        logger.debug(f"Headers: {headers}")
        if 'params' in kwargs:
            logger.debug(f"Query Params: {kwargs['params']}")
        if 'json' in kwargs:
            logger.debug(f"Request Body (JSON): {kwargs['json']}")
        if 'data' in kwargs:
             logger.debug(f"Request Body (Data): {kwargs['data']}")

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=timeout,
                **kwargs
            )
            logger.debug(f"Response Status Code: {response.status_code}")
            # 尝试记录响应体，不是json格式的响应则记录文本
            try:
                logger.trace(f"Response Body (JSON): {response.json()}")
            except requests.exceptions.JSONDecodeError:
                logger.trace(f"Response Body (Non-JSON): {response.text}")
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

        #封装常用的HTTP方法
    def get(self, endpoint,params=None, **kwargs):
        """发送 GET 请求"""
        return self._send_request('GET', endpoint, params=params,**kwargs)
    
    def post(self, endpoint, json=None, data=None, **kwargs):
        """发送 POST 请求"""
        return self._send_request('POST', endpoint, json=json, data=data, **kwargs)
    
    def put(self, endpoint, json=None, data=None, **kwargs):
        return self._send_request('put', endpoint, json=json, data=data, **kwargs)

    def patch(self, endpoint, json=None, data=None, **kwargs):
        return self._send_request('patch', endpoint, json=json, data=data, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self._send_request('delete', endpoint, **kwargs)

# 创建一个实例，方便其他模块导入后直接使用
# 如果希望每次使用都是新实例，可以在 fixture 中创建
api_client = ApiClient()
