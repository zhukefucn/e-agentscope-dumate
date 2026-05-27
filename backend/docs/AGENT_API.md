# Agent API 使用文档

## 概述

Agent 管理模块提供了完整的 CRUD 操作，用于管理 AI Agent 配置。

## API 端点

### 基础路径
```
/api/agents
```

### 认证
所有端点都需要 JWT Token 认证，在请求头中添加：
```
Authorization: Bearer <your_token>
```

---

## 1. 获取 Agent 列表

**GET** `/api/agents`

### 查询参数
- `skip` (可选): 跳过的记录数，默认 0
- `limit` (可选): 返回的最大记录数，默认 100

### 响应示例
```json
{
  "total": 2,
  "agents": [
    {
      "id": 1,
      "name": "智能助手",
      "description": "一个友好的AI助手",
      "system_prompt": "你是一个友好、专业的AI助手。",
      "model_provider": "dashscope",
      "model_name": "qwen-plus",
      "tools": [],
      "temperature": 0.7,
      "max_tokens": 2000,
      "user_id": 1,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ]
}
```

---

## 2. 创建 Agent

**POST** `/api/agents`

### 请求体
```json
{
  "name": "智能助手",
  "description": "一个友好的AI助手",
  "system_prompt": "你是一个友好、专业的AI助手，致力于帮助用户解决问题。",
  "model_provider": "dashscope",
  "model_name": "qwen-plus",
  "tools": [
    {
      "name": "search",
      "description": "搜索工具",
      "parameters": {}
    }
  ],
  "temperature": 0.7,
  "max_tokens": 2000
}
```

### 字段说明
- `name` (必需): Agent 名称，1-100 字符
- `description` (可选): Agent 描述，最多 500 字符
- `system_prompt` (必需): 系统提示词
- `model_provider` (必需): 模型提供商
  - `dashscope` - 通义千问
  - `openai` - OpenAI
  - `deepseek` - DeepSeek
  - `ollama` - Ollama
  - `custom` - 其他 OpenAI 兼容模型
- `model_name` (必需): 模型名称
  - dashscope: `qwen-plus`, `qwen-turbo`, `qwen-max`
  - openai: `gpt-4`, `gpt-3.5-turbo`
  - deepseek: `deepseek-chat`, `deepseek-coder`
  - ollama: `llama2`, `codellama`
- `tools` (可选): 工具配置列表，JSON 数组
- `temperature` (可选): 温度参数，0.0-2.0，默认 0.7
- `max_tokens` (可选): 最大 token 数，1-32000，默认 2000

### 响应示例
```json
{
  "id": 1,
  "name": "智能助手",
  "description": "一个友好的AI助手",
  "system_prompt": "你是一个友好、专业的AI助手，致力于帮助用户解决问题。",
  "model_provider": "dashscope",
  "model_name": "qwen-plus",
  "tools": [],
  "temperature": 0.7,
  "max_tokens": 2000,
  "user_id": 1,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

---

## 3. 获取单个 Agent

**GET** `/api/agents/{agent_id}`

### 路径参数
- `agent_id`: Agent ID

### 响应示例
```json
{
  "id": 1,
  "name": "智能助手",
  "description": "一个友好的AI助手",
  "system_prompt": "你是一个友好、专业的AI助手。",
  "model_provider": "dashscope",
  "model_name": "qwen-plus",
  "tools": [],
  "temperature": 0.7,
  "max_tokens": 2000,
  "user_id": 1,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

---

## 4. 更新 Agent

**PUT** `/api/agents/{agent_id}`

### 路径参数
- `agent_id`: Agent ID

### 请求体（所有字段可选）
```json
{
  "name": "更新后的助手",
  "description": "更新后的描述",
  "temperature": 0.8
}
```

### 响应示例
```json
{
  "id": 1,
  "name": "更新后的助手",
  "description": "更新后的描述",
  "system_prompt": "你是一个友好、专业的AI助手。",
  "model_provider": "dashscope",
  "model_name": "qwen-plus",
  "tools": [],
  "temperature": 0.8,
  "max_tokens": 2000,
  "user_id": 1,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T01:00:00"
}
```

---

## 5. 删除 Agent

**DELETE** `/api/agents/{agent_id}`

### 路径参数
- `agent_id`: Agent ID

### 响应
- 状态码: 204 No Content
- 无响应体

---

## 错误响应

### 404 Not Found
```json
{
  "detail": "Agent with id 999 not found"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

---

## 使用示例

### Python (使用 requests)
```python
import requests

BASE_URL = "http://localhost:8000/api"
TOKEN = "your_jwt_token"

headers = {"Authorization": f"Bearer {TOKEN}"}

# 创建 Agent
agent_data = {
    "name": "智能助手",
    "description": "一个友好的AI助手",
    "system_prompt": "你是一个友好、专业的AI助手。",
    "model_provider": "dashscope",
    "model_name": "qwen-plus",
    "temperature": 0.7,
    "max_tokens": 2000
}

response = requests.post(f"{BASE_URL}/agents", json=agent_data, headers=headers)
agent = response.json()
print(f"Created agent: {agent['id']}")

# 获取 Agent 列表
response = requests.get(f"{BASE_URL}/agents", headers=headers)
agents = response.json()
print(f"Total agents: {agents['total']}")

# 更新 Agent
update_data = {"temperature": 0.8}
response = requests.put(f"{BASE_URL}/agents/{agent['id']}", json=update_data, headers=headers)
updated_agent = response.json()
print(f"Updated temperature: {updated_agent['temperature']}")

# 删除 Agent
response = requests.delete(f"{BASE_URL}/agents/{agent['id']}", headers=headers)
print(f"Deleted agent: {response.status_code == 204}")
```

### cURL
```bash
# 获取 Agent 列表
curl -X GET "http://localhost:8000/api/agents" \
  -H "Authorization: Bearer your_token"

# 创建 Agent
curl -X POST "http://localhost:8000/api/agents" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "智能助手",
    "description": "一个友好的AI助手",
    "system_prompt": "你是一个友好、专业的AI助手。",
    "model_provider": "dashscope",
    "model_name": "qwen-plus",
    "temperature": 0.7,
    "max_tokens": 2000
  }'

# 获取单个 Agent
curl -X GET "http://localhost:8000/api/agents/1" \
  -H "Authorization: Bearer your_token"

# 更新 Agent
curl -X PUT "http://localhost:8000/api/agents/1" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{"temperature": 0.8}'

# 删除 Agent
curl -X DELETE "http://localhost:8000/api/agents/1" \
  -H "Authorization: Bearer your_token"
```

---

## 数据库模型

### Agent 表结构
```sql
CREATE TABLE agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    system_prompt TEXT NOT NULL,
    model_provider VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    tools TEXT,  -- JSON string
    temperature FLOAT DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 2000,
    user_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 注意事项

1. **认证**: 所有 API 都需要有效的 JWT Token
2. **权限**: 用户只能访问自己创建的 Agent
3. **工具配置**: `tools` 字段存储为 JSON 字符串，API 会自动序列化/反序列化
4. **模型提供商**: 支持主流模型提供商，可扩展其他 OpenAI 兼容模型
5. **参数验证**: 
   - `temperature`: 0.0-2.0
   - `max_tokens`: 1-32000
   - `name`: 1-100 字符
   - `description`: 最多 500 字符
