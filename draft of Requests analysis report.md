# Requests 库软件工程分析

## 1. 需求分析（用户想要解决哪些问题）

### 主要用例场景

#### **用例1：简单的HTTP请求**
```python
# 用户需求：快速发送GET请求获取数据
response = requests.get('https://api.example.com/data')
print(response.json())
```
**解决的问题**：
- 避免复杂的 `urllib` 设置
- 自动处理连接管理
- 简化响应解析

#### **用例2：带有复杂参数的请求**
```python
# 用户需求：发送带认证、参数和文件的POST请求
files = {'file': open('report.pdf', 'rb')}
data = {'key': 'value'}
auth = ('user', 'pass')
response = requests.post('https://api.example.com/upload', 
                         files=files, data=data, auth=auth)
```
**解决的问题**：
- 多部分表单编码自动化
- 认证处理
- 参数序列化

#### **用例3：会话管理（保持状态）**
```python
# 用户需求：在多个请求间保持Cookie和Session
with requests.Session() as s:
    s.auth = ('user', 'pass')
    s.headers.update({'x-test': 'true'})
    s.get('https://httpbin.org/cookies/set/sessioncookie/123456789')
    r = s.get('https://httpbin.org/cookies')
```
**解决的问题**：
- Cookie持久化
- 连接复用提高性能
- 统一配置管理

#### **用例4：错误处理和重试**
```python
# 用户需求：自动处理网络异常
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
```
**解决的问题**：
- 网络波动容错
- 连接超时重试
- 优雅降级

## 2. 设计分析（设计模式和架构）

### **整体架构模式**
```
         ┌─────────────────┐
         │   User Code     │
         └────────┬────────┘
                  │ (调用)
         ┌────────▼────────┐
         │   API Layer     │ ←─── 外观模式(Facade)
         │    (api.py)     │
         └────────┬────────┘
                  │ (委托)
         ┌────────▼────────┐
         │ Session Layer   │ ←─── 单例模式(Session as Singleton)
         │ (sessions.py)   │
         └────────┬────────┘
                  │ (转换)
         ┌────────▼────────┐
         │  Model Layer    │ ←─── 建造者模式(PreparedRequest构建)
         │  (models.py)    │
         └────────┬────────┘
                  │ (适配)
         ┌────────▼────────┐
         │ Adapter Layer   │ ←─── 适配器模式(HTTPAdapter)
         │ (adapters.py)   │
         └────────┬────────┘
                  │ (委托)
         ┌────────▼────────┐
         │   Urllib3       │
         └─────────────────┘
```

### **各模块设计模式分析**

#### **api.py - 外观模式(Facade Pattern)**
```python
# 为复杂的Session系统提供简单接口
def get(url, **kwargs):
    return request('get', url, **kwargs)  # 隐藏内部复杂性
```
**设计目的**：
- 提供简洁、一致的API
- 隐藏Session创建的复杂性
- 确保资源正确释放（with语句）

#### **sessions.py - 会话模式(Session Pattern)**
```python
class Session:
    def __init__(self):
        self.headers = default_headers()    # 统一配置
        self.cookies = cookiejar_from_dict({})  # 状态保持
        self.adapters = OrderedDict()       # 策略注册
```
**设计目的**：
- 维护跨请求的状态
- 配置管理集中化
- 连接复用优化

#### **models.py - 建造者模式(Builder Pattern)**
```python
# Request → PreparedRequest 的逐步构建
class PreparedRequest:
    def prepare(self, method=None, url=None, ...):
        self.prepare_method(method)    # 步骤1
        self.prepare_url(url, params)  # 步骤2
        self.prepare_headers(headers)  # 步骤3
        # ... 更多步骤
```
**设计目的**：
- 复杂对象的逐步构建
- 分离请求的创建和表示
- 支持不同的请求构建方式

#### **models.py - 混入模式(Mixin Pattern)**
```python
class RequestEncodingMixin:    # 功能混入
    @staticmethod
    def _encode_params(data):
        # 编码逻辑
        
class RequestHooksMixin:       # 钩子混入
    def register_hook(self, event, hook):
        # 钩子管理
```
**设计目的**：
- 功能组合而非继承
- 代码复用
- 灵活的功能扩展

#### **adapters.py - 适配器模式(Adapter Pattern)**
```python
class HTTPAdapter(BaseAdapter):  # 适配urllib3
    def send(self, request, stream=False, ...):
        # 将requests请求适配为urllib3请求
        conn = self.get_connection_with_tls_context(...)
        resp = conn.urlopen(...)  # 调用urllib3
        return self.build_response(request, resp)
```
**设计目的**：
- 统一不同HTTP库的接口
- 支持可替换的传输实现
- 抽象网络细节

#### **sessions.py - 策略模式(Strategy Pattern)**
```python
# 根据URL选择不同的适配器
def get_adapter(self, url):
    for prefix, adapter in self.adapters.items():
        if url.lower().startswith(prefix.lower()):
            return adapter  # 返回匹配的适配器策略
```
**设计目的**：
- 运行时选择算法
- 支持不同的协议处理
- 易于扩展新协议

## 3. 具体实现分析（用例解决流程）

### **用例1解决流程：简单GET请求**

#### **调用链分析**
```python
# 用户代码
response = requests.get('https://api.example.com/users')

# 实际调用流程：
1. api.py: get(url, **kwargs)
   ↓
2. api.py: request('get', url, **kwargs)
   ↓
3. sessions.py: Session().__enter__()  # 创建会话
   ↓
4. sessions.py: Session().request('GET', url, ...)
   ↓
5. sessions.py: Request()  # 创建请求对象
   ↓
6. sessions.py: prepare_request()  # 准备请求
   ↓
7. models.py: PreparedRequest.prepare()  # 构建完整请求
   ↓
8. sessions.py: send() → get_adapter()  # 获取适配器
   ↓
9. adapters.py: HTTPAdapter.send()  # 发送请求
   ↓
10. adapters.py: conn.urlopen()  # urllib3实际发送
   ↓
11. adapters.py: build_response()  # 构建响应
   ↓
12. sessions.py: Session().__exit__()  # 清理资源
```

#### **关键文件交互**
```python
# api.py 简化接口
def get(url, params=None, **kwargs):
    return request('get', url, params=params, **kwargs)

def request(method, url, **kwargs):
    # 使用上下文管理确保资源清理
    with sessions.Session() as session:
        return session.request(method=method, url=url, **kwargs)

# sessions.py 会话管理
class Session:
    def request(self, method, url, **kwargs):
        # 1. 创建请求对象
        req = Request(method=method, url=url, **kwargs)
        
        # 2. 准备请求（合并配置）
        prep = self.prepare_request(req)
        
        # 3. 合并环境设置
        settings = self.merge_environment_settings(...)
        
        # 4. 发送请求
        resp = self.send(prep, **settings)
        return resp
    
    def prepare_request(self, request):
        # 合并会话和请求配置
        merged_cookies = merge_cookies(self.cookies, request.cookies)
        merged_auth = merge_setting(request.auth, self.auth)
        merged_headers = merge_setting(request.headers, self.headers)
        
        # 构建PreparedRequest
        p = PreparedRequest()
        p.prepare(
            method=request.method,
            url=request.url,
            headers=merged_headers,
            auth=merged_auth,
            cookies=merged_cookies,
            # ... 其他参数
        )
        return p

# models.py 请求构建
class PreparedRequest:
    def prepare(self, method=None, url=None, params=None, ...):
        # 逐步构建请求
        self.prepare_method(method)
        self.prepare_url(url, params)    # 处理URL和参数
        self.prepare_headers(headers)    # 处理头部
        self.prepare_cookies(cookies)    # 处理Cookie
        self.prepare_body(data, files, json)  # 处理请求体
        
        # 支持多种数据格式
        if json is not None:
            body = complexjson.dumps(json)  # JSON序列化
        elif files:
            body, content_type = self._encode_files(files, data)  # 文件上传
        elif data:
            body = self._encode_params(data)  # 表单编码

# adapters.py 网络传输
class HTTPAdapter:
    def send(self, request, stream=False, timeout=None, ...):
        # 1. 获取连接（支持代理）
        conn = self.get_connection_with_tls_context(
            request, verify, proxies=proxies, cert=cert
        )
        
        # 2. SSL证书验证
        self.cert_verify(conn, request.url, verify, cert)
        
        # 3. 准备URL（处理代理情况）
        url = self.request_url(request, proxies)
        
        # 4. 通过urllib3发送
        resp = conn.urlopen(
            method=request.method,
            url=url,
            body=request.body,
            headers=request.headers,
            timeout=timeout,
            # ... 其他参数
        )
        
        # 5. 构建Response对象
        return self.build_response(request, resp)
```

### **用例2解决流程：文件上传和认证**

#### **复杂参数处理**
```python
# 用户代码
files = {'file': ('report.pdf', open('report.pdf', 'rb'), 'application/pdf')}
data = {'title': 'Monthly Report'}
response = requests.post(url, files=files, data=data, auth=('user', 'pass'))

# 处理流程：
1. models.py: PreparedRequest.prepare_body()
   ↓
2. models.py: _encode_files()  # 多部分编码
   ↓
3. urllib3.filepost: encode_multipart_formdata()  # 实际编码
   ↓
4. models.py: prepare_auth() → HTTPBasicAuth  # 认证处理
   ↓
5. adapters.py: cert_verify()  # 如有HTTPS，验证证书
```

#### **多部分表单编码实现**
```python
# models.py - 文件编码逻辑
def _encode_files(files, data):
    new_fields = []
    
    # 处理普通字段
    for field, val in fields:
        new_fields.append((field, str(v).encode('utf-8')))
    
    # 处理文件字段
    for k, v in files:
        if isinstance(v, (tuple, list)):
            if len(v) == 2:
                fn, fp = v  # (filename, fileobj)
            elif len(v) == 3:
                fn, fp, ft = v  # 带Content-Type
            else:
                fn, fp, ft, fh = v  # 带自定义头部
        
        # 创建multipart字段
        rf = RequestField(name=k, data=fdata, filename=fn, headers=fh)
        rf.make_multipart(content_type=ft)
        new_fields.append(rf)
    
    # 编码为multipart/form-data
    body, content_type = encode_multipart_formdata(new_fields)
    return body, content_type
```

### **用例3解决流程：会话状态管理**

#### **Cookie持久化实现**
```python
# sessions.py - Cookie管理
class Session:
    def send(self, request, **kwargs):
        # 发送请求
        r = adapter.send(request, **kwargs)
        
        # 保存Cookie（关键步骤）
        extract_cookies_to_jar(self.cookies, request, r.raw)
        
        # 如果重定向，也保存历史请求的Cookie
        if r.history:
            for resp in r.history:
                extract_cookies_to_jar(self.cookies, resp.request, resp.raw)
        
        return r

# models.py - Cookie提取
def extract_cookies_to_jar(jar, request, response):
    # 从响应头提取Set-Cookie
    # 添加到CookieJar
    # 根据domain/path规则存储
```

#### **配置合并机制**
```python
# sessions.py - 智能配置合并
def merge_setting(request_setting, session_setting, dict_class=OrderedDict):
    """合并请求级和会话级配置"""
    
    # 请求级配置优先
    if request_setting is None:
        return session_setting
    if session_setting is None:
        return request_setting
    
    # 字典类型深度合并
    if isinstance(session_setting, Mapping) and isinstance(request_setting, Mapping):
        merged = dict_class(session_setting)
        merged.update(request_setting)
        
        # 删除显式设为None的项
        for k in [k for (k, v) in merged.items() if v is None]:
            del merged[k]
        
        return merged
    
    # 非字典类型直接使用请求配置
    return request_setting
```

### **用例4解决流程：错误处理和重试**

#### **重试机制实现**
```python
# adapters.py - 重试集成
class HTTPAdapter:
    def __init__(self, max_retries=DEFAULT_RETRIES, ...):
        if max_retries == DEFAULT_RETRIES:
            self.max_retries = Retry(0, read=False)
        else:
            self.max_retries = Retry.from_int(max_retries)
        # ... 其他初始化

    def send(self, request, ...):
        try:
            resp = conn.urlopen(
                method=request.method,
                # ... 其他参数
                retries=self.max_retries,  # 传递重试策略
                timeout=timeout,
            )
        except MaxRetryError as e:
            # 转换urllib3异常为requests异常
            if isinstance(e.reason, ConnectTimeoutError):
                raise ConnectTimeout(e, request=request)
            # ... 其他异常转换
```

#### **异常层次结构**
```python
# exceptions.py - 统一的异常体系
class RequestException(IOError):          # 基类
    pass

class ConnectionError(RequestException):   # 连接错误
    pass

class Timeout(RequestException):           # 超时
    pass

class HTTPError(RequestException):         # HTTP错误
    pass

# 用户友好的错误处理
try:
    response = requests.get(url, timeout=5)
    response.raise_for_status()  # 检查HTTP状态码
except requests.exceptions.Timeout:
    print("请求超时")
except requests.exceptions.HTTPError as err:
    print(f"HTTP错误: {err}")
except requests.exceptions.RequestException as err:
    print(f"请求异常: {err}")
```

## 设计总结

### **设计原则体现**

1. **单一职责原则**
   - `api.py`: 只提供公共API接口
   - `sessions.py`: 只管理会话状态
   - `models.py`: 只定义数据模型
   - `adapters.py`: 只处理网络传输

2. **开闭原则**
   - 可通过继承 `BaseAdapter` 创建新适配器
   - 可通过 `mount()` 注册新协议处理器
   - 可通过钩子系统扩展功能

3. **依赖倒置原则**
   - 高层模块不依赖低层细节
   - 通过抽象接口通信（`BaseAdapter`）
   - 依赖注入配置

4. **接口隔离原则**
   - 用户只需要 `api.py` 的简单接口
   - 高级用户可使用 `Session` 完整接口
   - 扩展开发者使用适配器接口

### **工程优势**

1. **渐进式复杂度**
   - 初学者：只用 `requests.get()`
   - 中级用户：使用 `Session` 和参数
   - 高级用户：自定义适配器和重试策略

2. **可测试性**
   - 各模块可独立测试
   - 可Mock网络层
   - 清晰的接口便于单元测试

3. **可维护性**
   - 模块化设计
   - 清晰的关注点分离
   - 良好的异常处理

这个架构使得 `requests` 库既简单易用，又足够强大和灵活，能够满足从简单脚本到复杂企业应用的各种需求。