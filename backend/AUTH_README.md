# E-AgentScope 用户认证模块

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── auth.py          # 认证 API 路由
│   ├── core/
│   │   ├── config.py        # 配置文件
│   │   ├── database.py      # 数据库配置
│   │   └── security.py      # 安全工具（密码哈希、JWT）
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # 用户数据库模型
│   │   ├── agent.py         # Agent 模型
│   │   └── conversation.py  # 对话模型
│   └── schemas/
│       ├── __init__.py
│       └── user.py          # 用户 Pydantic 模型
├── main.py                  # 应用入口
├── requirements.txt         # 依赖包
└── test_auth.py            # 测试脚本
```

## 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

## 运行应用

```bash
# 开发模式
python main.py

# 或者使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API 文档

启动应用后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 1. 用户注册
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "securepassword123"
}
```

### 2. 用户登录
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "securepassword123"
}
```

响应：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. 获取当前用户信息
```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

## 使用示例

### Python 客户端

```python
import httpx

BASE_URL = "http://localhost:8000"

# 注册
response = httpx.post(f"{BASE_URL}/api/auth/register", json={
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
})
print(response.json())

# 登录
response = httpx.post(f"{BASE_URL}/api/auth/login", json={
    "username": "testuser",
    "password": "testpassword123"
})
token = response.json()["access_token"]

# 获取用户信息
response = httpx.get(
    f"{BASE_URL}/api/auth/me",
    headers={"Authorization": f"Bearer {token}"}
)
print(response.json())
```

### cURL

```bash
# 注册
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpassword123"}'

# 登录
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpassword123"}'

# 获取用户信息（替换 YOUR_TOKEN）
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 测试

运行测试脚本创建测试用户：

```bash
python test_auth.py
```

## 配置

在 `.env` 文件中可以配置：

```env
# JWT 配置
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7天

# 数据库
DATABASE_URL=sqlite+aiosqlite:///./eagentscope.db
```

## 技术栈

- **FastAPI**: 现代、快速的 Web 框架
- **SQLAlchemy 2.0**: 异步 ORM
- **SQLite**: 轻量级数据库
- **JWT**: JSON Web Token 认证
- **bcrypt**: 密码哈希
- **Pydantic**: 数据验证
