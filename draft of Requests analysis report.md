# Requests 库软件工程分析

## 1. 需求分析（核心用例与解决的问题）

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
- 简化响应解析（自动JSON解码）
- 统一异常处理

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
- 认证处理（Basic Auth, Digest Auth等）
- 参数序列化（表单/JSON自动转换）
- 文件上传简化

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
- Cookie持久化（自动处理Set-Cookie）
- 连接复用提高性能（HTTP Keep-Alive）
- 统一配置管理（头信息、认证等）
- TCP连接池管理

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
- 网络波动容错（连接超时、DNS失败等）
- 连接超时重试（可配置重试策略）
- 优雅降级（部分失败不影响整体）
- 统一的异常体系

## 2. 设计分析（设计模式与架构）

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
         │ Session Layer   │ ←─── 会话模式(Session) + 策略模式(Strategy)
         │ (sessions.py)   │
         └────────┬────────┘
                  │ (构建)
         ┌────────▼────────┐
         │  Model Layer    │ ←─── 建造者模式(Builder) + 混入模式(Mixin)
         │  (models.py)    │
         └────────┬────────┘
                  │ (适配)
         ┌────────▼────────┐
         │ Adapter Layer   │ ←─── 适配器模式(Adapter) + 享元模式(Flyweight)
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

def request(method, url, **kwargs):
    # 使用上下文管理器确保资源正确释放
    with sessions.Session() as session:
        return session.request(method=method, url=url, **kwargs)
```
**设计目的**：
- 提供简洁、一致的API（7个HTTP方法对应7个函数）
- 隐藏Session创建和资源管理的复杂性
- 确保资源正确释放（通过with语句）
- 提供向后兼容的工厂方法

#### **sessions.py - 多模式组合设计**
```python
# 会话模式(Session Pattern) + 策略模式(Strategy Pattern) + 桥接模式(Bridge Pattern)
class Session:
    def __init__(self):
        self.headers = default_headers()    # 统一配置
        self.cookies = cookiejar_from_dict({})  # 状态保持
        self.adapters = OrderedDict()       # 策略注册表
        self.mount('https://', HTTPAdapter())  # 默认策略注册
        self.mount('http://', HTTPAdapter())
    
    # 策略模式：运行时选择适配器
    def get_adapter(self, url):
        for prefix, adapter in self.adapters.items():
            if url.lower().startswith(prefix.lower()):
                return adapter  # 返回匹配的策略
    
    # 桥接模式：将请求桥接到具体实现
    def send(self, request, **kwargs):
        adapter = self.get_adapter(request.url)  # 选择实现
        return adapter.send(request, **kwargs)   # 委托给实现
```

#### **models.py - 建造者模式(Builder Pattern)**
```python
# Request → PreparedRequest 的逐步构建
class PreparedRequest:
    def prepare(self, method=None, url=None, ...):
        # 清晰的构建步骤序列
        self.prepare_method(method)    # 步骤1：构建HTTP方法
        self.prepare_url(url, params)  # 步骤2：构建URL和查询参数
        self.prepare_headers(headers)  # 步骤3：构建头部信息
        self.prepare_cookies(cookies)  # 步骤4：构建Cookie
        self.prepare_body(data, files, json)  # 步骤5：构建请求体
        self.prepare_auth(auth, url)   # 步骤6：构建认证信息
        self.prepare_hooks(hooks)      # 步骤7：构建钩子
        
        # 返回完整构建的对象
        return self
    
    # 模板方法模式：定义URL准备的算法骨架
    def prepare_url(self, url, params):
        # 步骤1：URL编码和规范化
        # 步骤2：参数编码和合并
        # 步骤3：IDNA编码处理
        # 步骤4：最终URL构建
```

#### **models.py - 混入模式(Mixin Pattern)**
```python
# 功能混入：通过多重继承组合功能
class RequestEncodingMixin:    # 编码功能混入
    @staticmethod
    def _encode_params(data):
        # 参数编码逻辑（表单编码）
        
    @staticmethod
    def _encode_files(files, data):
        # 文件编码逻辑（multipart/form-data）

class RequestHooksMixin:       # 钩子功能混入
    def register_hook(self, event, hook):
        # 钩子注册（观察者模式实现）
        
    def deregister_hook(self, event, hook):
        # 钩子注销

# 组合使用混入
class PreparedRequest(RequestEncodingMixin, RequestHooksMixin):
    # 继承两个混入类的功能
    pass
```

#### **adapters.py - 适配器模式(Adapter Pattern)**
```python
class BaseAdapter:  # 目标接口
    def send(self, request, stream=False, timeout=None, ...):
        raise NotImplementedError

class HTTPAdapter(BaseAdapter):  # 适配器实现
    def send(self, request, stream=False, timeout=None, ...):
        # 1. 将requests请求适配为urllib3请求
        conn = self.get_connection_with_tls_context(...)
        
        # 2. 调用urllib3的urlopen方法
        resp = conn.urlopen(
            method=request.method,  # 方法映射
            url=self.request_url(request, proxies),  # URL映射
            body=request.body,      # 请求体映射
            headers=request.headers, # 头部映射
            # ... 其他参数映射
        )
        
        # 3. 将urllib3响应适配为requests响应
        return self.build_response(request, resp)
```

#### **享元模式(Flyweight Pattern) - 连接池实现**
```python
class HTTPAdapter:
    def __init__(self, pool_connections=DEFAULT_POOLSIZE, ...):
        self.init_poolmanager(pool_connections, pool_maxsize, ...)
    
    def init_poolmanager(self, connections, maxsize, **pool_kwargs):
        """享元工厂：创建并管理连接池共享对象"""
        self.poolmanager = PoolManager(
            num_pools=connections,  # 连接池数量
            maxsize=maxsize,        # 每个池最大连接数
            **pool_kwargs
        )
    
    def get_connection_with_tls_context(self, request, verify, ...):
        """享元获取：从池中获取或创建共享连接"""
        # 构建连接键（host, port, scheme等）
        host_params, pool_kwargs = self.build_connection_pool_key_attributes(...)
        
        if proxy:
            # 获取代理连接享元
            proxy_manager = self.proxy_manager_for(proxy)
            conn = proxy_manager.connection_from_host(**host_params)
        else:
            # 获取直连连接享元
            conn = self.poolmanager.connection_from_host(**host_params)
        
        return conn  # 返回共享连接对象
```

## 3. 具体实现分析（用例解决流程）

### **用例1解决流程：简单GET请求**

#### **调用链与关键交互**
```python
# 用户代码
response = requests.get('https://api.example.com/users')

# 实际调用流程：
1. api.py: get(url, **kwargs)  ← 外观模式入口
   ↓
2. api.py: request('get', url, **kwargs)
   ↓
3. sessions.py: Session().__enter__()  ← 创建会话（上下文管理器）
   ↓
4. sessions.py: Session().request('GET', url, ...)  ← 会话处理
   ↓
5. sessions.py: Request()  ← 创建请求对象
   ↓
6. sessions.py: prepare_request()  ← 配置合并
   ↓
7. models.py: PreparedRequest.prepare()  ← 建造者模式构建
   ↓
8. sessions.py: send() → get_adapter()  ← 策略模式选择适配器
   ↓
9. adapters.py: HTTPAdapter.send()  ← 适配器模式发送
   ↓
10. urllib3: conn.urlopen()  ← 实际网络传输
   ↓
11. adapters.py: build_response()  ← 构建响应对象
   ↓
12. sessions.py: extract_cookies_to_jar()  ← Cookie持久化
   ↓
13. sessions.py: Session().__exit__()  ← 资源清理
```

#### **核心实现细节**
```python
# api.py - 外观实现
def request(method, url, **kwargs):
    """核心外观方法：封装整个请求生命周期"""
    # 使用上下文管理器确保资源正确释放
    with sessions.Session() as session:
        return session.request(method=method, url=url, **kwargs)

# sessions.py - 配置合并机制
def merge_setting(request_setting, session_setting, dict_class=OrderedDict):
    """智能配置合并：请求级配置优先于会话级配置"""
    if request_setting is None:
        return session_setting
    if session_setting is None:
        return request_setting
    
    # 字典类型深度合并
    if isinstance(session_setting, Mapping) and isinstance(request_setting, Mapping):
        merged = dict_class(to_key_val_list(session_setting))
        merged.update(to_key_val_list(request_setting))
        
        # 删除显式设为None的项（允许用户覆盖后取消设置）
        for k in [k for (k, v) in merged.items() if v is None]:
            del merged[k]
        
        return merged
    
    # 非字典类型直接使用请求配置
    return request_setting

# adapters.py - 响应构建
def build_response(self, req, resp):
    """将urllib3响应适配为requests响应"""
    response = Response()
    
    # 状态码和头部映射
    response.status_code = getattr(resp, 'status', None)
    response.headers = CaseInsensitiveDict(getattr(resp, 'headers', {}))
    
    # 编码自动检测
    response.encoding = get_encoding_from_headers(response.headers)
    
    # 原始响应和URL
    response.raw = resp
    response.url = req.url.decode('utf-8') if isinstance(req.url, bytes) else req.url
    
    # Cookie提取
    extract_cookies_to_jar(response.cookies, req, resp)
    
    # 请求上下文
    response.request = req
    response.connection = self
    
    return response
```

### **用例2解决流程：文件上传和认证**

#### **复杂参数处理流程**
```python
# 用户代码
files = {'file': ('report.pdf', open('report.pdf', 'rb'), 'application/pdf')}
data = {'title': 'Monthly Report'}
response = requests.post(url, files=files, data=data, auth=('user', 'pass'))

# 处理流程：
1. models.py: PreparedRequest.prepare_body()
   ↓
2. models.py: _encode_files()  ← 多部分编码（混入模式）
   ↓
3. urllib3.filepost: encode_multipart_formdata()  ← 实际编码
   ↓
4. models.py: prepare_auth() → HTTPBasicAuth  ← 认证处理
   ↓
5. adapters.py: cert_verify()  ← SSL证书验证
   ↓
6. adapters.py: 构建multipart请求体并发送
```

#### **多部分表单编码实现**
```python
def _encode_files(files, data):
    """多部分表单编码：支持多种文件格式"""
    new_fields = []
    
    # 处理普通表单字段
    for field, val in to_key_val_list(data or {}):
        if isinstance(val, basestring) or not hasattr(val, '__iter__'):
            val = [val]
        for v in val:
            if v is not None:
                new_fields.append((
                    field.decode('utf-8') if isinstance(field, bytes) else field,
                    v.encode('utf-8') if isinstance(v, str) else v
                ))
    
    # 处理文件字段（支持多种格式）
    for k, v in to_key_val_list(files or {}):
        # 支持4种文件格式：
        # 1. 文件对象
        # 2. (filename, fileobj)
        # 3. (filename, fileobj, content_type)
        # 4. (filename, fileobj, content_type, custom_headers)
        if isinstance(v, (tuple, list)):
            if len(v) == 2:
                fn, fp = v
                ft = None
                fh = None
            elif len(v) == 3:
                fn, fp, ft = v
                fh = None
            else:
                fn, fp, ft, fh = v
        else:
            fn = guess_filename(v) or k
            fp = v
            ft = None
            fh = None
        
        # 读取文件数据
        if isinstance(fp, (str, bytes, bytearray)):
            fdata = fp
        elif hasattr(fp, 'read'):
            fdata = fp.read()
        elif fp is None:
            continue
        else:
            fdata = fp
        
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
# sessions.py - Cookie管理机制
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

# models.py - Cookie提取和存储
def extract_cookies_to_jar(jar, request, response):
    """从响应中提取Cookie并存储到CookieJar"""
    # 获取响应头中的Set-Cookie
    # 解析Cookie属性（domain, path, expires等）
    # 根据domain/path规则存储到CookieJar
    # 支持RFC 6265标准
```

#### **连接复用机制**
```python
# adapters.py - 连接池管理
class HTTPAdapter:
    def init_poolmanager(self, connections, maxsize, **pool_kwargs):
        """初始化连接池：HTTP Keep-Alive实现"""
        self.poolmanager = PoolManager(
            num_pools=connections,  # 不同host的池数量
            maxsize=maxsize,        # 每个host的最大连接数
            block=self._pool_block,
            **pool_kwargs
        )
    
    def get_connection_with_tls_context(self, request, verify, ...):
        """从池中获取或创建连接"""
        # 构建连接键（scheme, host, port）
        host_params = {
            'scheme': scheme,
            'host': parsed_request_url.hostname,
            'port': port,
        }
        
        # 从连接池获取连接（享元模式）
        conn = self.poolmanager.connection_from_host(**host_params)
        
        return conn  # 复用的TCP连接
```

### **用例4解决流程：错误处理和重试**

#### **重试机制实现**
```python
# adapters.py - 重试策略集成
class HTTPAdapter:
    def __init__(self, max_retries=DEFAULT_RETRIES, ...):
        if max_retries == DEFAULT_RETRIES:
            self.max_retries = Retry(0, read=False)  # 默认不重试
        else:
            # 支持urllib3的Retry对象或整数值
            self.max_retries = Retry.from_int(max_retries)
    
    def send(self, request, ...):
        try:
            resp = conn.urlopen(
                method=request.method,
                url=url,
                body=request.body,
                headers=request.headers,
                retries=self.max_retries,  # 传递重试策略
                timeout=timeout,
                # ... 其他参数
            )
        except MaxRetryError as e:
            # 异常转换：将urllib3异常转换为requests异常
            if isinstance(e.reason, ConnectTimeoutError):
                raise ConnectTimeout(e, request=request)
            elif isinstance(e.reason, _ProxyError):
                raise ProxyError(e, request=request)
            elif isinstance(e.reason, _SSLError):
                raise SSLError(e, request=request)
            else:
                raise ConnectionError(e, request=request)
```

#### **统一异常体系**
```python
# exceptions.py - 层次化异常设计
class RequestException(IOError):          # 根异常
    """所有requests异常的基类"""
    pass

class ConnectionError(RequestException):   # 连接相关错误
    """网络连接错误"""
    pass

class Timeout(RequestException):           # 超时错误
    """请求超时"""
    pass

class HTTPError(RequestException):         # HTTP协议错误
    """HTTP错误响应（4xx, 5xx）"""
    pass

class SSLError(RequestException):          # SSL/TLS错误
    """SSL证书验证失败"""
    pass

# 使用示例
try:
    response = requests.get(url, timeout=5)
    response.raise_for_status()  # 自动检查HTTP状态码
except requests.exceptions.Timeout:
    print("请求超时")
except requests.exceptions.SSLError:
    print("SSL证书验证失败")
except requests.exceptions.RequestException as err:
    print(f"请求失败: {err}")
```

## 4. 设计总结

Requests 库通过精心组合多种设计模式，实现了简单易用与强大灵活的统一：

### **架构优势**
1. **渐进式复杂度**：从简单的 `requests.get()` 到复杂的自定义适配器，满足不同层次需求
2. **高度可扩展**：通过适配器、策略、钩子等模式支持功能扩展
3. **性能优化**：连接池、Cookie持久化、连接复用等机制提升性能
4. **强健性**：统一的异常体系、完善的错误处理和重试机制

### **模式协同**
- **外观+建造者**：为用户提供简单API，内部使用建造者构建复杂对象
- **策略+适配器**：运行时选择传输策略，适配不同底层实现
- **享元+会话**：连接池复用资源，会话管理保持状态
- **混入+观察者**：功能灵活组合，钩子系统支持扩展

### **工程价值**
Requests 库不仅是Python HTTP客户端的标准，更是优秀软件设计的典范。其设计模式的应用展示了如何将复杂系统分解为可维护、可扩展的组件，同时保持API的简洁性和易用性。这种设计思想值得在构建类似复杂系统时借鉴。