# PeopleScope

PeopleScope 是一个基于 Python 的多智能体（Multi-Agent）应用程序，旨在通过一系列智能对话和分析来深入理解和描绘用户画像。

## ✨ 主要功能

- **对话交互**: 通过 `ChatAgent` 与用户进行实时对话。
- **动态问题生成**: `QuestionGenerateAgent` 能够根据对话上下文生成相关问题，以引导对话和收集信息。
- **用户标签生成**: `UserTagGenerateAgent` 分析对话内容，为用户生成描述性的标签或特征。
- **反思与洞察**: `ReflectionAgent` 对用户的回答和行为进行深层分析，提供反思和洞察。
- **信息聚合**: `AggregateAgent` 汇总所有收集到的信息，形成一个全面的用户画像（"Scope"）。

## 🚀 快速开始

请按照以下步骤在本地环境中设置和运行项目。

### 1. 先决条件

- Python 3.8+
- Pip 包管理器
- 一个可用的数据库 (例如 MySQL, PostgreSQL)

### 2. 安装

首先，克隆本项目到本地：
```bash
git clone <your-repository-url>
cd PeopleScope
```

**重要提示**: 项目中缺少 `requirements.txt` 文件。您可以通过以下命令生成它，或者手动添加所有依赖项。
```bash
pip freeze > requirements.txt
```

接下来，安装所有依赖：
```bash
pip install -r requirements.txt
```

### 3. 环境配置

项目使用 `.env` 文件来管理环境变量。请复制或重命名 `.env.example` (如果存在) 为 `.env`，并填入必要的配置，例如数据库连接信息和外部 API 密钥。

```dotenv
# .env
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=people_scope

# 如果使用了大模型服务，请填入 API Key
LLM_API_KEY=your_api_key
```

### 4. 运行项目

配置完成后，通过以下命令启动应用：

```bash
python api/PeopleScopeApi.py
```

服务将会在本地启动，您可以通过指定的端口访问 API。

## 🏛️ 项目架构

项目采用分层架构，确保代码的模块化和可维护性。

- **`api/`**: API 入口层，负责处理 HTTP 请求和响应。使用 `PeopleScopeApi.py` 作为主入口。
- **`service/`**: 服务层，包含核心业务逻辑。每个服务对应一个特定的业务领域（如 `ChatService`, `UserService`）。
- **`agent/`**: 智能体层，封装了与大语言模型（LLM）交互的逻辑，是实现智能分析的核心。
- **`repository/`**: 数据仓库层，负责与数据库进行交互，实现了数据访问的抽象。
- **`model/`**: 数据模型层，定义了应用中的核心数据结构（如 `User`, `Chat`, `Session`）。
- **`schema/`**: 模式定义层，用于 API 的数据验证和序列化/反序列化。
- **`core/`**: 核心组件，包括数据库连接、配置加载和日志记录等。
- **`static/`**: 存放静态文件，如 `index.html`。

## 📁 目录结构

```
.
├── agent/            # 智能体
├── api/              # API 接口
├── core/             # 核心配置 (数据库, 日志)
├── model/            # 数据模型
├── repository/       # 数据仓库 (数据库操作)
├── schema/           # API 数据模式
├── service/          # 业务逻辑服务
├── static/           # 静态文件
└── .env              # 环境变量
```

## 🤝 如何贡献

欢迎对项目做出贡献！请遵循以下步骤：

1.  Fork 本仓库
2.  创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3.  提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4.  推送到分支 (`git push origin feature/AmazingFeature`)
5.  提交一个 Pull Request

## 📄 许可证

本项目采用 [MIT](https://choosealicense.com/licenses/mit/) 许可证。
