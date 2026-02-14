"""
用例3：会话管理（保持状态）
追踪 Session 中多个请求的 Cookie 持久化、连接复用等机制。
输出合并到 usecase3_trace.log，每个函数 depth=5 限制内部行数。
"""

import pysnooper
import requests

LOG_FILE = 'usecase3_trace.log'

# ------------------ 装饰目标函数 ------------------
# Session初始化
original_session_init = requests.sessions.Session.__init__

@pysnooper.snoop(output=LOG_FILE, depth=5, prefix='[SessionInit] ')
def traced_session_init(self, *args, **kwargs):
    return original_session_init(self, *args, **kwargs)

requests.sessions.Session.__init__ = traced_session_init

# Session.request
original_session_request = requests.sessions.Session.request

@pysnooper.snoop(output=LOG_FILE, depth=5, prefix='[SessionReq] ')
def traced_session_request(self, method, url, **kwargs):
    return original_session_request(self, method, url, **kwargs)

requests.sessions.Session.request = traced_session_request

# HTTPAdapter.send
original_adapter_send = requests.adapters.HTTPAdapter.send

@pysnooper.snoop(output=LOG_FILE, depth=5, prefix='[Adapter] ')
def traced_adapter_send(self, request, *args, **kwargs):
    return original_adapter_send(self, request, *args, **kwargs)

requests.adapters.HTTPAdapter.send = traced_adapter_send

# Cookie提取
from requests.cookies import extract_cookies_to_jar

@pysnooper.snoop(output=LOG_FILE, depth=5, prefix='[Cookie] ')
def traced_extract_cookies_to_jar(jar, request, response):
    return extract_cookies_to_jar(jar, request, response)

requests.cookies.extract_cookies_to_jar = traced_extract_cookies_to_jar

# ------------------ 执行用例 ------------------
print("开始执行用例3：会话管理")

with requests.Session() as s:
    s.auth = ('user', 'pass')
    s.headers.update({'x-test': 'true'})
    
    resp1 = s.get('https://httpbin.org/cookies/set/sessioncookie/123456789')
    print("第一个请求状态码:", resp1.status_code)
    
    resp2 = s.get('https://httpbin.org/cookies')
    print("第二个请求状态码:", resp2.status_code)
    print("返回的Cookies:", resp2.json())

print(f"追踪日志已写入 {LOG_FILE}")