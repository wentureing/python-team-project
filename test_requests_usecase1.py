"""
用例1：简单GET请求
追踪从 requests.get() 到 urllib3 网络调用的完整流程。
输出合并到 usecase1_trace.log，每个函数 depth=5 限制内部行数。
"""

import pysnooper
import requests

# 统一输出文件
LOG_FILE = 'usecase1_trace.log'

# ------------------ 装饰目标函数 ------------------
# API层：requests.get
original_get = requests.api.get

@pysnooper.snoop(output=LOG_FILE, depth=5, prefix='[API] ')
def traced_get(url, **kwargs):
    return original_get(url, **kwargs)

requests.api.get = traced_get

# 会话层：Session.request
original_session_request = requests.sessions.Session.request

@pysnooper.snoop(output=LOG_FILE, depth=5, prefix='[Session] ')
def traced_session_request(self, method, url, **kwargs):
    return original_session_request(self, method, url, **kwargs)

requests.sessions.Session.request = traced_session_request

# 适配器层：HTTPAdapter.send
original_adapter_send = requests.adapters.HTTPAdapter.send

@pysnooper.snoop(output=LOG_FILE, depth=5, prefix='[Adapter] ')
def traced_adapter_send(self, request, *args, **kwargs):
    return original_adapter_send(self, request, *args, **kwargs)

requests.adapters.HTTPAdapter.send = traced_adapter_send

# ------------------ 执行用例 ------------------
print("开始执行用例1：简单GET请求")
response = requests.get('https://httpbin.org/get')
print("状态码:", response.status_code)
print("响应JSON:", response.json())
print(f"追踪日志已写入 {LOG_FILE}")