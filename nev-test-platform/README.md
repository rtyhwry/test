# 新能源汽车测试平台 (NEV Test Platform)

一个面向新能源汽车研发测试领域的自动化测试管理平台，提供完整的测试任务调度、环境管理、测试执行和报告生成能力。

## 🚀 功能特性

### 核心功能
- **任务调度管理**：支持立即执行、定时执行、周期执行(Cron)等多种调度方式
- **环境管理**：测试主机和测试设备的统一管理，支持环境锁定和自动释放
- **制品集成**：从制品库拉取软件版本，自动升级测试设备
- **代码集成**：从GitLab拉取测试代码到测试主机
- **ALM集成**：同步ALM平台的测试任务和用例，回写执行结果
- **测试报告**：自动生成HTML/PDF/Excel格式报告，支持趋势分析

### 技术架构
- **后端**：Django 5.0 + Django REST Framework + Celery
- **前端**：Vue 3 + Element Plus + ECharts
- **数据库**：PostgreSQL 15
- **消息队列**：Redis 7 + Celery
- **部署**：Docker + Docker Compose

## 📁 项目结构

```
nev-test-platform/
├── backend/                    # Django后端
│   ├── apps/                   # 应用模块
│   │   ├── users/              # 用户认证
│   │   ├── projects/           # 项目管理
│   │   ├── hosts/              # 主机管理
│   │   ├── devices/            # 设备管理
│   │   ├── environments/       # 环境管理
│   │   ├── artifacts/          # 制品管理
│   │   ├── tasks/              # 任务调度
│   │   ├── testcases/          # 测试用例
│   │   ├── reports/            # 测试报告
│   │   └── integrations/       # 第三方集成
│   ├── config/                 # 项目配置
│   └── requirements.txt
├── frontend/                   # Vue前端
│   ├── src/
│   │   ├── api/                # API接口
│   │   ├── components/         # 组件
│   │   ├── layouts/            # 布局
│   │   ├── router/             # 路由
│   │   ├── stores/             # 状态管理
│   │   └── views/              # 页面
│   └── package.json
├── docker/                     # Docker配置
├── docs/                       # 文档
├── docker-compose.yml          # 生产部署配置
└── docker-compose.dev.yml      # 开发环境配置
```

## 🛠️ 快速开始

### 环境要求
- Docker & Docker Compose
- Node.js 18+ (本地开发)
- Python 3.11+ (本地开发)

### 使用Docker部署（推荐）

1. 克隆项目
```bash
git clone <repository-url>
cd nev-test-platform
```

2. 配置环境变量
```bash
cp backend/.env.example backend/.env
# 编辑 .env 文件，配置必要的环境变量
```

3. 启动服务
```bash
docker-compose up -d
```

4. 访问应用
- 前端界面: http://localhost
- API文档: http://localhost:8000/api/docs/
- 管理后台: http://localhost:8000/admin/
- Flower监控: http://localhost:5555

### 本地开发

1. 启动依赖服务
```bash
docker-compose -f docker-compose.dev.yml up -d
```

2. 启动后端
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

3. 启动Celery (另一个终端)
```bash
cd backend
celery -A config worker -l info
```

4. 启动前端
```bash
cd frontend
npm install
npm run dev
```

## 📖 API文档

启动服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

### 主要API端点

| 模块 | 端点 | 描述 |
|------|------|------|
| 认证 | `/api/v1/auth/` | 登录/登出/注册 |
| 用户 | `/api/v1/users/` | 用户管理 |
| 项目 | `/api/v1/projects/` | 项目管理 |
| 主机 | `/api/v1/hosts/` | 测试主机管理 |
| 设备 | `/api/v1/devices/` | 测试设备管理 |
| 环境 | `/api/v1/environments/` | 测试环境管理 |
| 制品 | `/api/v1/artifacts/` | 制品版本管理 |
| 任务 | `/api/v1/tasks/` | 测试任务管理 |
| 用例 | `/api/v1/testcases/` | 测试用例管理 |
| 报告 | `/api/v1/reports/` | 测试报告管理 |
| 集成 | `/api/v1/integrations/` | 第三方集成 |

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | Django密钥 | - |
| `DEBUG` | 调试模式 | False |
| `DB_HOST` | 数据库主机 | localhost |
| `DB_NAME` | 数据库名 | nev_test_platform |
| `REDIS_URL` | Redis地址 | redis://localhost:6379/1 |
| `GITLAB_URL` | GitLab地址 | - |
| `GITLAB_TOKEN` | GitLab Token | - |
| `ALM_URL` | ALM平台地址 | - |
| `ARTIFACT_REPO_URL` | 制品库地址 | - |

### 第三方集成配置

#### GitLab集成
用于拉取测试代码到测试主机。

```python
GITLAB_URL = "https://gitlab.example.com"
GITLAB_TOKEN = "your-private-token"
```

#### ALM集成
用于同步测试任务和用例，回写执行结果。

```python
ALM_URL = "https://alm.example.com"
ALM_USERNAME = "your-username"
ALM_PASSWORD = "your-password"
```

#### 制品库集成
用于获取软件版本并升级测试设备。

```python
ARTIFACT_REPO_URL = "https://nexus.example.com"
ARTIFACT_REPO_USERNAME = "your-username"
ARTIFACT_REPO_PASSWORD = "your-password"
```

## 📊 使用流程

### 典型测试流程

1. **创建项目** - 配置项目信息和Git仓库
2. **注册主机** - 添加测试执行主机，配置SSH连接
3. **注册设备** - 添加测试设备（ECU/VCU等）
4. **配置环境** - 创建测试环境，关联主机和设备
5. **同步制品** - 从制品库同步可用的软件版本
6. **创建任务** - 创建测试任务，配置调度策略
7. **添加用例** - 添加测试用例或从ALM同步
8. **执行任务** - 手动或自动触发任务执行
9. **查看报告** - 查看执行结果和测试报告

### 任务执行流程

```
创建任务 → 选择环境 → [升级设备] → 拉取代码 → 执行测试 → 收集结果 → 生成报告
```

## 🔐 权限说明

| 角色 | 权限 |
|------|------|
| admin | 全部权限，包括用户管理 |
| manager | 项目管理、任务管理、环境管理 |
| engineer | 执行任务、管理用例、查看报告 |
| viewer | 只读访问 |

## 📝 开发指南

### 添加新的App

```bash
cd backend
python manage.py startapp new_app apps/new_app
```

### 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 运行测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm run test
```

## 🐛 常见问题

**Q: 无法连接到测试主机?**
A: 检查SSH配置，确保主机可达且凭证正确。可以使用"测试连接"功能验证。

**Q: 任务执行超时?**
A: 调整任务的超时时间设置，默认为60分钟。

**Q: Celery任务不执行?**
A: 确保Celery Worker和Redis服务正常运行。检查Flower监控面板。

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request!
