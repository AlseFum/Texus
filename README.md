## 计划
port方面：
实现基本文字读写
实现复杂文字读写
实现只读即时信息
实现有限的脚本运行
实现极其复杂的权限管理
实现文件夹
express方面：
很多了

需要整理API和架构

#### 1. 最小单元的权限
```
可知权限
可读权限
    可读必可知
可写权限
    （相当于输入流
配置权
    可以配置某个资源除了写之外的属性，不能改变拥有权
拥有权
    可以分配配置权，可以取消拥有的对象需要的权限使其暴露于公众
自定义权限：
    基于某项上述操作，以支持默认行为
```
#### 权限组的权限
总管权
    可以管理管理，以及特定管理的行为
    总管对所有对象的权限就是所有用户对对象的权限
    可以配置组权限本身
管理权
    可以拉人，踢人，无限制分发token
    可以设置子组
用户
    有限的分发token，受规定的访问
脚本/智能体


### 权限模型

#### 角色定义 (Role)
```python
@dataclass
class Role:
    name: str                    # 角色名称
    description: str             # 角色描述
    permissions: List[Permission] # 权限列表
    inherits: List[str]          # 继承的角色
    is_system: bool             # 是否为系统角色
```

#### 权限定义 (Permission)
```python
@dataclass
class Permission:
    resource_type: ResourceType  # 资源类型
    resource_path: str          # 资源路径(支持通配符)
    action: Action              # 操作类型
    conditions: Dict[str, Any]  # 额外条件
```

#### 用户模型 (User)
```python
@dataclass
class User:
    id: str                     # 用户ID
    username: str               # 用户名
    email: str                  # 邮箱
    password_hash: str          # 密码哈希
    roles: List[str]            # 角色列表
    attributes: Dict[str, Any]  # 用户属性
    is_active: bool             # 是否激活
    created_at: datetime        # 创建时间
    last_login: datetime        # 最后登录时间
```

#### 访问令牌 (Token)
```python
@dataclass
class Token:
    token: str                  # 令牌字符串
    user_id: str                # 用户ID
    permissions: List[Permission] # 令牌权限
    expires_at: datetime        # 过期时间
    created_at: datetime        # 创建时间
    is_revoked: bool            # 是否撤销
    metadata: Dict[str, Any]    # 元数据
```

### 默认角色体系

#### 1. 访客角色 (guest)
- 只能访问公开内容
- 权限：`NOTE:*:READ` (条件：public=true)
- 权限：`API:/health:READ`

#### 2. 用户角色 (user)
- 普通用户权限
- 权限：`NOTE:*:READ`
- 权限：`NOTE:*:UPDATE` (条件：owner=true)
- 权限：`NOTE:*:DELETE` (条件：owner=true)
- 权限：`FOLDER:*:CREATE/READ/UPDATE/DELETE` (条件：owner=true)

#### 3. 脚本角色 (script)
- 脚本执行权限
- 权限：`NOTE:*:READ/UPDATE`
- 权限：`SCRIPT:*:EXECUTE`
- 权限：`API:*:READ`

#### 4. 管理员角色 (admin)
- 完整管理权限
- 权限：所有资源的`READ/UPDATE/DELETE`
- 权限：`SYSTEM:*:MANAGE`

### 权限检查流程

```
1. 请求到达 → 解析访问上下文
2. 提取用户信息 → 验证令牌
3. 获取用户角色 → 检查角色权限
4. 匹配资源路径 → 验证操作权限
5. 检查额外条件 → 返回权限结果
```

### 路径匹配规则

- `*`: 匹配所有路径
- `exact_path`: 精确匹配
- `prefix*`: 前缀匹配
- 支持多级路径：`folder/subfolder/*`

### 条件权限

权限可以包含额外条件：
```python
Permission(
    ResourceType.NOTE, 
    "private/*", 
    Action.READ, 
    {"owner": True, "department": "IT"}
)
```

### 权限管理器 (PermissionManager)

负责：
- 用户创建和认证
- 角色管理
- 令牌生成和验证
- 权限检查
- 密码哈希和验证

### 集成方案

#### 1. 中间件集成
在FastAPI路由前添加权限检查中间件：
```python
@app.middleware("http")
async def permission_middleware(request: Request, call_next):
    # 权限检查逻辑
    pass
```

#### 2. 装饰器集成
为特定路由添加权限装饰器：
```python
@require_permission(ResourceType.NOTE, "private/*", Action.READ)
async def get_private_note():
    pass
```

#### 3. 数据库集成
- 用户表：存储用户信息和角色关联
- 角色表：存储角色定义和权限
- 令牌表：存储访问令牌
- 权限表：存储细粒度权限规则

### 安全特性

1. **令牌过期机制**: 自动过期，支持刷新
2. **密码哈希**: SHA-256加密存储
3. **权限继承**: 角色可以继承其他角色权限
4. **细粒度控制**: 支持资源级别的精确控制
5. **条件权限**: 支持基于属性的动态权限
6. **审计日志**: 记录所有权限检查操作

### 扩展性

- **插件化**: 支持自定义权限检查器
- **多租户**: 支持组织级别的权限隔离
- **动态权限**: 支持运行时权限修改
- **API权限**: 支持API级别的细粒度控制

## 🔒 加密验证系统设计

### 加密验证架构

为了增强安全性，权限系统支持多层加密验证机制，包括密码加密、令牌加密和通信加密。

### 加密组件

#### 1. 加密算法支持
```python
class EncryptionAlgorithm(Enum):
    AES_256_GCM = "aes-256-gcm"      # 对称加密，推荐
    AES_128_GCM = "aes-128-gcm"      # 对称加密，轻量级
    RSA_2048 = "rsa-2048"            # 非对称加密
    RSA_4096 = "rsa-4096"            # 非对称加密，高安全
    CHACHA20_POLY1305 = "chacha20-poly1305"  # 流加密
```

#### 2. 密钥管理 (KeyManager)
```python
@dataclass
class EncryptionKey:
    key_id: str                      # 密钥标识符
    algorithm: EncryptionAlgorithm    # 加密算法
    key_data: bytes                  # 密钥数据
    created_at: datetime             # 创建时间
    expires_at: Optional[datetime]   # 过期时间
    is_active: bool                  # 是否激活
    version: int                     # 密钥版本
    metadata: Dict[str, Any]         # 元数据

class KeyManager:
    def __init__(self):
        self.keys: Dict[str, EncryptionKey] = {}
        self.current_key_id: str = ""
        self.key_rotation_interval: timedelta = timedelta(days=30)
    
    def generate_key(self, algorithm: EncryptionAlgorithm) -> EncryptionKey:
        """生成新密钥"""
        pass
    
    def rotate_key(self) -> str:
        """密钥轮换"""
        pass
    
    def get_current_key(self) -> EncryptionKey:
        """获取当前活跃密钥"""
        pass
    
    def get_key_by_id(self, key_id: str) -> Optional[EncryptionKey]:
        """根据ID获取密钥"""
        pass
```

#### 3. 加密服务 (EncryptionService)
```python
class EncryptionService:
    def __init__(self, key_manager: KeyManager):
        self.key_manager = key_manager
    
    def encrypt_password(self, password: str, key_id: str = None) -> str:
        """加密密码"""
        pass
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        pass
    
    def encrypt_token(self, token_data: dict) -> str:
        """加密令牌"""
        pass
    
    def decrypt_token(self, encrypted_token: str) -> Optional[dict]:
        """解密令牌"""
        pass
    
    def encrypt_sensitive_data(self, data: str, key_id: str = None) -> str:
        """加密敏感数据"""
        pass
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> Optional[str]:
        """解密敏感数据"""
        pass
```

### 密钥标识和版本管理

#### 1. 密钥标识符格式
```
格式: {algorithm}-{version}-{timestamp}
示例: aes-256-gcm-v1-20241201
      rsa-2048-v2-20241215
```

#### 2. 密钥版本控制
```python
@dataclass
class KeyVersion:
    key_id: str
    version: int
    algorithm: EncryptionAlgorithm
    created_at: datetime
    is_current: bool
    predecessor: Optional[str] = None  # 前一个版本
    successor: Optional[str] = None    # 下一个版本

class KeyVersionManager:
    def __init__(self):
        self.versions: Dict[str, List[KeyVersion]] = {}
    
    def add_version(self, key: EncryptionKey):
        """添加密钥版本"""
        pass
    
    def get_version_history(self, algorithm: str) -> List[KeyVersion]:
        """获取版本历史"""
        pass
    
    def rollback_to_version(self, algorithm: str, version: int) -> bool:
        """回滚到指定版本"""
        pass
```

### 密文更换机制

#### 1. 自动密钥轮换
```python
class AutoKeyRotation:
    def __init__(self, key_manager: KeyManager, rotation_interval: timedelta):
        self.key_manager = key_manager
        self.rotation_interval = rotation_interval
        self.last_rotation = datetime.now()
    
    def should_rotate(self) -> bool:
        """检查是否需要轮换密钥"""
        return datetime.now() - self.last_rotation >= self.rotation_interval
    
    def rotate_if_needed(self) -> bool:
        """如果需要则执行密钥轮换"""
        if self.should_rotate():
            return self.force_rotate()
        return False
    
    def force_rotate(self) -> bool:
        """强制密钥轮换"""
        pass
```

#### 2. 手动密钥更换
```python
class ManualKeyRotation:
    def __init__(self, encryption_service: EncryptionService):
        self.encryption_service = encryption_service
    
    def create_new_key(self, algorithm: EncryptionAlgorithm) -> str:
        """创建新密钥"""
        pass
    
    def migrate_data(self, old_key_id: str, new_key_id: str) -> bool:
        """迁移数据到新密钥"""
        pass
    
    def validate_migration(self, old_key_id: str, new_key_id: str) -> bool:
        """验证迁移结果"""
        pass
```

### 加密令牌格式

#### 1. JWT格式扩展
```json
{
  "header": {
    "alg": "A256GCM",
    "typ": "JWT",
    "kid": "aes-256-gcm-v1-20241201"
  },
  "payload": {
    "sub": "user_id",
    "iat": 1701234567,
    "exp": 1701320967,
    "permissions": [...],
    "key_version": 1
  },
  "signature": "encrypted_signature"
}
```

#### 2. 自定义加密格式
```
格式: {key_id}.{encrypted_data}.{iv}.{tag}
示例: aes-256-gcm-v1-20241201.encrypted_data.iv.tag
```

### 安全策略

#### 1. 密钥生命周期管理
- **生成**: 使用安全的随机数生成器
- **存储**: 密钥分离存储，使用硬件安全模块(HSM)
- **轮换**: 定期自动轮换，支持手动触发
- **销毁**: 安全删除过期密钥

#### 2. 加密强度配置
```python
@dataclass
class SecurityConfig:
    min_key_length: int = 256        # 最小密钥长度
    key_rotation_days: int = 30      # 密钥轮换周期
    max_key_versions: int = 5        # 最大保留版本数
    encryption_algorithm: str = "aes-256-gcm"
    hash_algorithm: str = "sha-256"
    salt_rounds: int = 100000        # 密码盐值轮数
```

#### 3. 审计和监控
```python
@dataclass
class EncryptionAudit:
    operation: str                   # 操作类型
    key_id: str                      # 使用的密钥ID
    algorithm: str                   # 加密算法
    timestamp: datetime              # 操作时间
    user_id: str                     # 操作用户
    success: bool                    # 操作是否成功
    error_message: Optional[str]     # 错误信息
```

### 集成到权限系统

#### 1. 增强的用户认证
```python
class EnhancedUser(User):
    password_hash: str               # 加密后的密码
    encryption_key_id: str           # 使用的加密密钥ID
    password_version: int            # 密码版本
    last_password_change: datetime   # 最后修改时间
```

#### 2. 增强的令牌
```python
class EncryptedToken(Token):
    encryption_key_id: str           # 加密密钥ID
    encrypted_permissions: str       # 加密的权限数据
    key_version: int                 # 密钥版本
    is_encrypted: bool               # 是否已加密
```

#### 3. 权限检查增强
```python
class EnhancedPermissionManager(PermissionManager):
    def __init__(self, encryption_service: EncryptionService):
        super().__init__()
        self.encryption_service = encryption_service
        self.key_manager = encryption_service.key_manager
    
    def create_encrypted_token(self, user: User, permissions: List[Permission]) -> EncryptedToken:
        """创建加密令牌"""
        pass
    
    def validate_encrypted_token(self, token_str: str) -> Optional[EncryptedToken]:
        """验证加密令牌"""
        pass
```

### 配置示例

#### 1. 加密配置
```yaml
encryption:
  default_algorithm: "aes-256-gcm"
  key_rotation_days: 30
  max_key_versions: 5
  password_salt_rounds: 100000
  
  algorithms:
    aes-256-gcm:
      key_length: 256
      iv_length: 12
      tag_length: 16
    rsa-2048:
      key_length: 2048
      padding: "OAEP"
```

#### 2. 密钥管理配置
```yaml
key_management:
  storage_type: "database"  # database, file, hsm
  backup_enabled: true
  backup_interval: "daily"
  hsm_config:
    provider: "aws-kms"
    region: "us-west-2"
```

### 迁移策略

#### 1. 渐进式迁移
1. 部署新的加密系统
2. 新用户使用新加密方式
3. 现有用户登录时自动迁移
4. 逐步淘汰旧加密方式

#### 2. 回滚机制
- 保留旧密钥用于解密
- 支持版本回滚
- 数据完整性验证

这个加密验证系统提供了完整的密钥管理、版本控制和密文更换功能，确保系统的安全性和可维护性。
