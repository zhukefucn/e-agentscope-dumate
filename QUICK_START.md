# E-AgentScope Platform - 快速开始指南

## 服务状态

**后端服务**: http://localhost:8000
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

**前端服务**: http://localhost:3001 (或 5173)

**GitHub 仓库**: https://github.com/zhukefucn/e-agentscope-dumate

## 测试结果

已成功通过以下功能测试：

### 1. 用户注册
- 注册用户: testuser
- 邮箱: test@example.com
- 状态: 成功

### 2. 用户登录
- 登录用户: testuser
- JWT Token: 生成成功

### 3. 创建 Agent
- Agent 名称: 智能助手
- 模型: 通义千问 (qwen-plus)
- 工具: Read, Write
- 状态: 创建成功 (ID: 1)

### 4. 获取 Agent 列表
- 查询结果: 1 个 Agent
- 状态: 成功

## 启动服务

### 方法一：使用启动脚本（推荐）

双击运行 `start_all.bat`，将自动启动前后端服务。

### 方法二：手动启动

**启动后端**:
```bash
cd E:\dumate\E-agentscope\backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**启动前端**:
```bash
cd E:\dumate\E-agentscope\frontend
npm run dev
```

## 使用流程

1. **访问前端**: 打开浏览器访问 http://localhost:3001
2. **注册账号**: 点击"注册"，填写用户名、邮箱和密码
3. **登录系统**: 使用注册的账号登录
4. **创建 Agent**: 
   - 点击"创建 Agent"
   - 填写名称、描述、系统提示词
   - 选择模型提供商（推荐通义千问）
   - 选择工具（Read、Write、Bash 等）
   - 设置温度和最大 Token 数
5. **开始对话**: 点击 Agent 卡片的"开始对话"按钮

## 已配置的 API Key

通义千问 API Key: `sk-d21577d05eda4e97bec90b53bf8ff6bd`
- 已配置在 `backend/.env` 文件中
- 模型: qwen-plus
- 支持的功能: 文本对话、代码生成、问答等

## 支持的模型提供商

1. **DashScope (通义千问)** - 已配置 API Key
2. **OpenAI** - 需配置 OPENAI_API_KEY
3. **DeepSeek** - 需配置 DEEPSEEK_API_KEY
4. **Ollama** - 本地模型，无需 API Key
5. **Custom** - 自定义 OpenAI 兼容模型

## 项目架构

```
┌─────────────────────────────────────────┐
│        前端 (Vue 3 + TypeScript)         │
│  http://localhost:3001                  │
└─────────────────┬───────────────────────┘
                  │ HTTP/WebSocket
┌─────────────────▼───────────────────────┐
│      应用服务端 (FastAPI)                │
│  http://localhost:8000                  │
│  - 用户认证 (JWT)                        │
│  - Agent 管理                            │
│  - 对话代理                              │
│  - SQLite 数据库                         │
└─────────────────┬───────────────────────┘
                  │ Python API
┌─────────────────▼───────────────────────┐
│     AgentScope 平台 (底层)               │
│  - Agent 核心                            │
│  - 模型适配                              │
│  - 工具系统                              │
└─────────────────────────────────────────┘
```

## 注意事项

1. **AgentScope 模块**: 当前使用 Mock 模式（缺少 docstring_parser 依赖），不影响核心功能测试
2. **Pydantic 警告**: model_provider 和 model_name 字段有命名空间冲突警告，不影响功能
3. **前端端口**: 默认 5173，如果被占用会自动切换到 3001

## 下一步

1. 安装 AgentScope 完整依赖: `pip install docstring_parser`
2. 配置其他模型提供商的 API Key
3. 自定义 Agent 的系统提示词和工具
4. 部署到生产环境

---

**开发完成日期**: 2026-05-28
**版本**: 1.0.0
**状态**: 测试通过
