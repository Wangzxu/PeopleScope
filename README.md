# PeopleScope

PeopleScope 是一个基于 Python 的多智能体（Multi-Agent）人格分析与对话系统，旨在通过深度的智能交互，构建精准、动态的用户画像。系统集成了 LangChain、FastAPI、ChromaDB 等技术，实现了从即时对话到长期记忆的完整认知链路。

## ✨ 核心特性

- **🧠 智能长期记忆 (Long-Term Memory)**:
    - **事实提取**: 能够从对话中自动提取关于用户的关键事实（如偏好、经历、性格特征），而非简单存储原始对话流。
    - **记忆去重**: 引入向量相似度检测机制，避免重复存储相似信息，确保存储库的高效与纯净。
    - **上下文增强**: 在每次对话中智能检索最相关的 3 条历史事实，赋予 Agent 连贯的个性化记忆能力。

- **💬 深度对话交互**: 通过 `ChatAgent` 与用户进行自然、流畅的对话，能够根据用户画像动态调整回复风格。

- **📊 全维度用户画像**:
    - **Tags 生成**: `UserTagGenerateAgent` 基于对话内容自动生成用户风格与话题标签。
    - **人格聚合**: `AggregateAgent` 综合多维度信息，持续迭代用户的十维人格模型。
    - **深度反思**: `ReflectionAgent` 对每一轮交互进行元认知分析，提炼深层洞察。

- **⚙️ 专业级工程架构**:
    - **标准化日志**: 采用集中式日志管理，提供清晰、专业的系统运行状态监控。
    - **依赖注入**: 基于 Container 模式的依赖注入，确保组件解耦与易于测试。

## 🚀 快速开始

### 1. 环境准备

- Python 3.9+
- MySQL (结构化数据存储)
- MongoDB (文档型数据存储)
- ChromaDB (向量记忆存储 - 本地文件模式)

### 2. 安装

克隆项目并安装依赖：
```bash
git clone <your-repository-url>
cd PeopleScope
pip install -r requirements.txt
```

### 3. 配置

复制 `.env.example` 为 `.env` 并填入配置：

```dotenv
# LLM
OPENAI_API_KEY=your_api_key

# MySQL
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=password
DB_NAME=people_scope

# MongoDB
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB_NAME=people_scope_mongo

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Logger
LOG_LEVEL=INFO
LOG_DIR=logs
```

### 4. 运行

启动 API 服务：
```bash
python main.py
```
服务默认运行在 `http://127.0.0.1:8080`。

## 🏛️ 系统架构

项目采用清晰的分层架构：

- **`api/`**: **接口层**。处理 HTTP 请求，统一响应格式，集成全局日志与异常处理。
- **`service/`**: **业务逻辑层**。编排 Agent 与 Repository，实现核心业务流程（如 `ChatService` 负责协调对话生成与记忆存储）。
- **`agent/`**: **智能体层**。封装 LLM 交互逻辑，定义 Prompt 模板与输出解析（如 `ChatAgent` 负责事实提取与回复生成）。
- **`repository/`**: **数据访问层**。屏蔽底层数据库差异，提供统一的数据操作接口（支持 MySQL, Mongo, Chroma）。
- **`model/` & `schema/`**: **数据模型层**。定义数据库实体与 API 交互对象 (DTO)。
- **`core/`**: **核心组件**。包含数据库连接池、全局配置、日志工厂 (`logger.py`) 与依赖注入容器 (`container.py`)。

## 📁 目录结构

```
.
├── agent/            # 智能体实现 (LangChain Agents)
├── api/              # FastAPI 路由定义
├── core/             # 核心基础设施 (DB, Logger, Config)
├── model/            # SQLAlchemy ORM 模型
├── repository/       # 数据访问对象 (DAO)
├── schema/           # Pydantic 数据验证模型
├── service/          # 业务逻辑服务
├── static/           # 前端静态资源
├── main.py           # 程序入口
└── .env              # 环境变量配置
```

## 🤝 贡献指南

1.  Fork 本仓库
2.  创建特性分支 (`git checkout -b feature/NewFeature`)
3.  提交更改 (`git commit -m 'Add NewFeature'`)
4.  推送到分支 (`git push origin feature/NewFeature`)
5.  提交 Pull Request

## 📄 许可证

[MIT License](LICENSE)