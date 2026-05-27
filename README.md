# E-AgentScope Platform

企业级 Agent 服务平台，基于 AgentScope 框架构建的三层架构应用。

## 项目架构

```
┌─────────────────────────────────────────────────┐
│                   前端 (Vue 3)                    │
│  - 用户界面                                       │
│  - Agent 管理                                    │
│  - 对话交互                                       │
└─────────────────┬───────────────────────────────┘
                  │ HTTP/WebSocket
┌─────────────────▼───────────────────────────────┐
│              应用服务端 (FastAPI)                 │
│  - 用户认证 (JWT)                                │
│  - Agent 管理                                    │
│  - 对话代理                                      │
│  - 数据持久化 (SQLite)                           │
└─────────────────┬───────────────────────────────┘
                  │ Python API
┌─────────────────▼───────────────────────────────┐
│           AgentScope 平台 (底层)                  │
│  - Agent 核心                                    │
│  - 模型适配 (通义千问/OpenAI/DeepSeek/Ollama)    │
│  - 工具系统                                      │
└─────────────────────────────────────────────────┘
```

## 功能特性

### 用户管理
- 用户注册/登录
- JWT Token 认证
- 用户信息管理

### Agent 管理
- 创建自定义 Agent
- 配置系统提示词
- 选择模型提供商
- 配置工具集
- Agent 列表/编辑/删除

### 对话功能
- 实时对话
- 流式响应 (SSE)
- 对话历史管理
- Markdown 渲染
- 代码高亮

## 技术栈

### 后端
- **FastAPI** - 现代高性能 Web 框架
- **SQLAlchemy 2.0** - 异步 ORM
- **SQLite** - 轻量级数据库
- **JWT** - 身份认证
- **AgentScope** - Agent 框架

### 前端
- **Vue 3** - 渐进式 JavaScript 框架
- **TypeScript** - 类型安全
- **Vite** - 下一代前端构建工具
- **Element Plus** - Vue 3 UI 组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Axios** - HTTP 客户端
- **Marked** - Markdown 解析
- **Highlight.js** - 代码高亮

## 项目结构

```
E-agentscope/
├── agentscope-main/          # AgentScope 框架
│   └── src/agentscope/       # 核心源码
│
├── backend/                  # 应用服务端
│   ├── app/
│   │   ├── api/             # API 路由
│   │   │   ├── auth.py      # 认证接口
│   │   │   ├── agents.py    # Agent 管理
│   │   │   └── chat.py      # 对话接口
│   │   ├── models/          # 数据模型
│   │   ├── schemas/         # Pydantic 模型
│   │   ├── services/        # 业务逻辑
│   │   └── core/            # 核心配置
│   ├── main.py              # 应用入口
│   └── requirements.txt     # Python 依赖
│
├── frontend/                 # 前端应用
│   ├── src/
│   │   ├── views/           # 页面组件
│   │   ├── components/      # 公共组件
│   │   ├── services/        # API 服务
│   │   ├── stores/          # 状态管理
│   │   ├── types/           # 类型定义
│   │   └── router/          # 路由配置
│   ├── package.json         # Node 依赖
│   └── vite.config.ts       # Vite 配置
│
└── README.md
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- pnpm 或 npm

### 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（可选）
# 创建 .env 文件：
# DASHSCOPE_API_KEY=your-api-key-here

# 启动服务
python main.py

# 或使用 uvicorn
uvicorn main:app --reload --port 8000
```

后端服务将在 http://localhost:8000 启动

API 文档: http://localhost:8000/docs

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
pnpm install
# 或
npm install

# 启动开发服务器
pnpm dev
# 或
npm run dev
```

前端应用将在 http://localhost:5173 启动

### AgentScope 配置

如需使用真实 Agent 功能，需要配置 API Key：

1. **通义千问 (推荐)**
   ```bash
   export DASHSCOPE_API_KEY=your-dashscope-api-key
   ```

2. **OpenAI**
   ```bash
   export OPENAI_API_KEY=your-openai-api-key
   ```

3. **其他模型**
   - 在创建 Agent 时配置自定义 API Key

## API 接口

### 认证接口

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息

### Agent 接口

- `GET /api/agents` - 获取 Agent 列表
- `POST /api/agents` - 创建 Agent
- `GET /api/agents/{id}` - 获取 Agent 详情
- `PUT /api/agents/{id}` - 更新 Agent
- `DELETE /api/agents/{id}` - 删除 Agent

### 对话接口

- `POST /api/chat/conversations` - 创建对话
- `GET /api/chat/conversations` - 获取对话列表
- `GET /api/chat/conversations/{id}/messages` - 获取消息列表
- `POST /api/chat/conversations/{id}/messages` - 发送消息
- `DELETE /api/chat/conversations/{id}` - 删除对话

## 支持的模型

- **DashScope (通义千问)** - 默认推荐
- **OpenAI** - GPT 系列
- **DeepSeek** - DeepSeek 模型
- **Ollama** - 本地模型
- **自定义** - OpenAI 兼容模型

## 开发指南

### 数据库迁移

项目使用 SQLAlchemy 自动创建表结构，首次启动时会自动初始化数据库。

### 添加新模型提供商

1. 在 `backend/app/services/agentscope_client.py` 中添加模型配置
2. 在前端 `AgentCreate.vue` 中添加选项

### 自定义工具

AgentScope 支持多种内置工具：
- Bash - 执行 Shell 命令
- Read - 读取文件
- Write - 写入文件
- Edit - 编辑文件
- Grep - 搜索文件内容
- Glob - 查找文件

## 生产部署

### 后端部署

```bash
# 使用 gunicorn + uvicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 前端部署

```bash
# 构建
npm run build

# 使用 nginx 托管静态文件
```

### Docker 部署

```bash
# 构建镜像
docker build -t e-agentscope .

# 运行容器
docker run -p 8000:8000 e-agentscope
```

## 许可证

Apache-2.0

## 贡献

欢迎提交 Issue 和 Pull Request！
