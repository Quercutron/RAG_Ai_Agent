[DEVELOPMENT_DOC.md](https://github.com/user-attachments/files/30367168/DEVELOPMENT_DOC.md)
# RAG AI Agent — 扫地机器人智能客服 开发文档

## 一、项目概述

这是一个基于 **LangChain + Chroma + 通义千问** 的 RAG（检索增强生成）智能客服系统，面向扫地机器人/扫拖一体机器人领域。Agent 具备自主 ReAct 思考与工具调用能力，支持普通问答和个性化使用报告生成。

**技术栈**：Python 3.13、LangChain、LangGraph、Chroma、DashScope Embedding、Qwen Chat API

---

## 二、项目结构

```
RAG_AI_Agent/
├── config/                       # 配置文件层
│   ├── agent.yml                 # Agent 配置（外部数据路径）
│   ├── chroma.yml                # 向量库配置（chunk、k、阈值）
│   ├── prompts.yml               # 提示词文件路径配置
│   └── rag.yml                   # 模型配置（模型名、超时、重试）
│
├── model/                        # 模型工厂层
│   └── factory.py                # ChatOpenAI + DashScopeEmbeddings 工厂
│
├── utils/                        # 工具层
│   ├── config_handler.py         # YAML 配置加载器（模块级单例）
│   ├── file_handler.py           # 文档加载器（PDF/TXT）+ MD5 去重
│   ├── logger_handler.py         # 双通道日志（控制台 + 文件）
│   ├── path_tool.py              # 项目根目录绝对路径工具
│   └── prompt_loader.py          # 提示词文件加载器
│
├── rag/                          # RAG 核心层
│   ├── vector_store.py           # 向量存储服务（Chroma 管理 + 检索）
│   ├── rag_service.py            # RAG 总结服务（检索 → 拼接 → 生成）
│   └── chroma_db/                # Chroma 向量库持久化文件
│
├── agent/                        # Agent 层
│   ├── react_agent.py            # ReAct Agent 入口（create_agent）
│   └── tools/
│       ├── agent_tools.py        # 7 个工具定义 + 外部 CSV 数据加载
│       └── middleware.py         # 3 个中间件（监控 + 动态 prompt）
│
├── data/                         # 知识库数据层
│   ├── *.txt / *.pdf             # 扫地机器人 FAQ（选购、故障、维护、保养）
│   └── external/
│       └── records.csv           # 用户使用记录（10用户 × 12个月）
│
├── prompts/                      # 提示词模板层
│   ├── main_prompts.txt          # 主系统提示词（~2100 字）
│   ├── rag_summarize.txt         # RAG 总结提示词
│   └── report_prompt.txt         # 报告生成提示词
│
├── logs/                         # 运行日志
├── .env                          # API Key 等环境变量
└── md5.text                      # 文件去重 MD5 记录
```

---

## 三、分层架构

```
┌──────────────────────────────────────────────────────────┐
│                    Agent 层 (入口)                        │
│              react_agent.py + middleware.py               │
│      创建 ReAct Agent，注入工具、中间件、系统提示词        │
└────────────────────┬─────────────────────────────────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
     ▼               ▼               ▼
┌─────────┐  ┌─────────────┐  ┌──────────────┐
│ 工具层   │  │  RAG 核心层  │  │  模型工厂层   │
│agent_   │  │rag_service  │  │ factory.py   │
│tools.py │  │vector_store │  │ ChatOpenAI   │
│ 7个工具  │  │  检索+总结   │  │ Embeddings   │
└────┬────┘  └──────┬──────┘  └──────┬───────┘
     │              │               │
     │    ┌─────────┘               │
     ▼    ▼                         ▼
┌────────────┐              ┌──────────────┐
│  数据层     │              │   配置层       │
│ data/*.txt │              │ config/*.yml  │
│ external/  │              │ prompts/*.txt │
│ records.csv│              │ .env          │
└────────────┘              └──────────────┘
```

---

## 四、开发流程

### 阶段一：项目初始化

```
1. 创建项目目录结构
2. 编写配置层（config/*.yml）
3. 编写工具层（utils/*.py）
4. 配置环境变量（.env）
```

#### 配置文件清单

| 文件 | 关键字段 | 说明 |
|------|----------|------|
| `rag.yml` | `chat_model_name`, `embedding_model_name`, `request_timeout`, `max_retries` | 模型选择与 API 参数 |
| `chroma.yml` | `collection_name`, `persist_directory`, `k`, `chunk_size`, `chunk_overlap`, `separators`, `similarity_threshold`, `max_chunk_chars`, `max_context_chars` | 向量库与检索配置 |
| `prompts.yml` | `main_prompts_path`, `rag_summarize_prompt_path`, `report_prompt_path` | 提示词文件路径 |
| `agent.yml` | `external_data_path` | Agent 配置 |

#### 环境变量 (.env)

```
QWEN_API_KEY=xxx            # 通义千问 API Key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
DASHSCOPE_API_KEY=xxx       # DashScope Embedding API Key
```

---

### 阶段二：模型工厂

**文件**：`model/factory.py`

**设计模式**：工厂方法模式

```
BaseModelFactory (ABC)
    ├── ChatModelFactory    → ChatOpenAI(通过 QWEN_BASE_URL 兼容 OpenAI 接口)
    └── EmbeddingModelFactory → DashScopeEmbeddings
```

**调用链**：
1. `load_dotenv()` 加载环境变量
2. 从 `rag.yml` 读取模型配置
3. 工厂实例化 → 模块级单例 `chat_model` + `embedding_model`

**关键点**：
- `request_timeout` 和 `max_retries` 防止 API 超时
- `base_url` 指向阿里云百炼 DashScope 兼容端点

---

### 阶段三：RAG 知识库构建（离线 / 非实时）

**文件**：`rag/vector_store.py`

**流程**：

```
1. listdir_with_allow_type()  扫描 data/ 目录，过滤允许的文件类型 (.pdf, .txt)
2. get_file_md5_hex()         计算文件 MD5 用于去重
3. check_md5_hex()            检查 md5.text 记录，已入库则跳过
4. text_loader / pdf_loader   将文件加载为 Document 对象列表
5. RecursiveCharacterTextSplitter  将 Document 切分为 chunk
6. Chroma.add_documents()     向量化并存入 Chroma 持久化
7. save_md5_hex()             记录文件 MD5 防重复
```

**分割参数**（`chroma.yml`）：

| 参数 | 值 | 说明 |
|------|-----|------|
| `chunk_size` | 200 | 每块最多 200 字符 |
| `chunk_overlap` | 20 | 块间重叠 20 字符 |
| `separators` | `\n\n → \n → 。！？ → 空格 → ""` | 优先按大粒度分隔符切分 |

**知识库数据**：6 个扫地机器人相关文档（选购指南、故障排除、维护保养、FAQ × 3）

---

### 阶段四：RAG 检索与总结服务

**文件**：`rag/rag_service.py`

**流程**：

```
用户查询 (query)
    │
    ▼
search_with_threshold(query)        ← 带相似度阈值过滤的检索
    │  similarity_threshold: 1.0
    ▼
context 构建                         ← 三重控制：
    │  ├─ ① 相似度过滤（score ≤ 1.0）
    │  ├─ ② 单chunk截断（≤ 150 chars）
    │  └─ ③ 总长限制（≤ 500 chars）
    ▼
PromptTemplate 拼接                   ← 基于 rag_summarize.txt 模板
    │
    ▼
ChatOpenAI (qwen-plus) → StrOutputParser
    │
    ▼
返回自然语言回答
```

**三重上下文控制机制**：

| 层 | 机制 | 配置项 | 作用 |
|----|------|--------|------|
| ① | 相似度过滤 | `similarity_threshold` | L2 距离大于阈值的 chunk 丢弃 |
| ② | 单 chunk 截断 | `max_chunk_chars: 150` | 每个参考资料最长 150 字 |
| ③ | 总长限制 | `max_context_chars: 500` | 总上下文不超过 500 字 |

---

### 阶段五：Agent 工具定义

**文件**：`agent/tools/agent_tools.py`

**7 个工具**：

| 工具名 | 入参 | 出参 | 说明 |
|--------|------|------|------|
| `get_summarize` | `query: str` | 总结文本 | 从向量库检索并总结 |
| `get_weather` | `city: str` | 天气信息 | 模拟天气查询 |
| `get_user_location` | 无 | 城市名 | 模拟定位 |
| `get_user_id` | 无 | 用户 ID | 模拟获取用户 |
| `get_current_month` | 无 | 月份 `2025-MM` | 模拟当前月份 |
| `fetch_external_data` | `user_id, month` | 使用记录 | 查询 CSV 中用户记录 |
| `fill_context_for_report` | 无 | 无 | 标记报告场景，触发中间件动态切换 prompt |

**外部数据加载**（`generate_external_data`）：

```
records.csv
    │  user_id + 特征 + 效率 + 耗材 + 对比 + 时间
    │  (10 用户 × 12 个月 = 120 条记录)
    ▼
external_data: dict
    {
        "1001": {
            "2025-01": {特征, 效率, 耗材, 对比},
            "2025-02": {...},
            ...
        },
        ...
    }
```

---

### 阶段六：中间件

**文件**：`agent/tools/middleware.py`

| 中间件 | 装饰器 | 功能 |
|--------|--------|------|
| `monitor_tool` | `@wrap_tool_call` | 工具调用前后日志记录；检测 `fill_context_for_report` 标记报告场景 |
| `log_before_model` | `@before_model` | 模型调用前记录当前对话轮次和最后一条消息 |
| `report_prompt_switch` | `@dynamic_prompt` | 根据 `runtime.context["report"]` 动态切换系统提示词 |

**动态 Prompt 切换流程**：

```
用户说"生成我的6月使用报告"
    → Agent 调用 fill_context_for_report
    → monitor_tool 捕获 → 设置 runtime.context["report"] = True
    → 下一轮模型调用前 → report_prompt_switch 返回 load_report_prompt()
    → 模型获得报告生成专用提示词
```

---

### 阶段七：ReAct Agent 组装

**文件**：`agent/react_agent.py`

```python
create_agent(
    model=chat_model,              # Qwen 聊天模型
    system_prompt=load_system_prompt(),  # main_prompts.txt
    tools=[7个工具],                # Agent 工具集
    middleware=[3个中间件],          # 监控 + 日志 + 动态 Prompt
)
```

**执行流程**：

```
用户输入
    │
    ▼
create_agent → ReAct 循环
    │
    ├─ 思考 (Thought) → 分析需求，判断是否需要工具
    ├─ 行动 (Action)  → 调用工具 (get_summarize / get_user_id / ...)
    ├─ 观察 (Observation) → 获取工具返回结果
    └─ 再思考 → 循环直到信息足够，生成最终回答
```

---

## 五、数据流全景

```
用户："扫地机器人怎么保养？"
    │
    ▼
react_agent.execute_stream()
    │  system_prompt = load_system_prompt()
    │  middleware = [monitor_tool, log_before_model, report_prompt_switch]
    ▼
ReAct Agent 思考
    │  判断需要调用 get_summarize 获取专业资料
    ▼
get_summarize("机器人保养")
    │
    ▼
rag_service.rag_summarize()
    │  search_with_threshold("机器人保养")
    │  Chroma.similarity_search_with_score(k=2)
    │  → 相似度过滤 → 截断 → 总长限制
    │  → PromptTemplate → ChatOpenAI → 总结
    ▼
Agent 获得总结资料 → 整合回答
    │
    ▼
返回："扫地机器人的保养主要注意以下几点：1.定期清理尘盒和滤网..."
```

---

## 六、关键设计决策

### 1. 工厂模式 + 模块级单例

`ChatOpenAI` 和 `DashScopeEmbeddings` 在模块加载时实例化一次，全局复用，避免重复创建连接。

### 2. MD5 文件去重

知识库加载时通过 MD5 判断文件是否已入库，防止重复向量化。

### 3. 相似度阈值过滤

不使用 `as_retriever()` 的无差别检索，改用 `similarity_search_with_score()` 按 L2 距离阈值过滤。

### 4. 三重上下文控制

相似度过滤 → 单 chunk 截断 → 总长度限制，三层控制防止 context 过长消耗过多 token。

### 5. 动态 Prompt 切换

通过中间件实现普通问答 / 报告生成两种场景的 Prompt 自动切换，无需用户手动指定。

---

## 七、已修复的Bug清单

| # | 问题 | 文件 | 修复 |
|---|------|------|------|
| 1 | `.generator()` 方法名不匹配 | `factory.py` | 统一为 `generator()` |
| 2 | `from logger_handler import logger` 缺少 `utils.` | `file_handler.py` | 补全包路径 |
| 3 | MD5 路径不一致（相对 vs 绝对） | `vector_store.py` | 统一使用 `get_abs_path()` |
| 4 | `split_document` 为空缺少 `continue` | `vector_store.py` | 补 `continue` |
| 5 | `listdir_with_allow_type` 错误返回后缀名元组 | `file_handler.py` | `return []` 代替 `return allow_types` |
| 6 | `separators` 含 `""` 导致字符级切分 | `chroma.yml` | 调整顺序，`""` 移至末尾 |
| 7 | `ChatOpenAI` 无超时配置 → API 超时 | `factory.py` | 加 `request_timeout` + `max_retries` |
| 8 | `.env` 不存在 → API URL 为空 | 项目根目录 | 创建 `.env` |
| 9 | `log_before_model` 空 messages 越界 | `middleware.py` | 加空列表守卫 |
| 10 | `react_agent` 空 messages 越界 | `react_agent.py` | 加空列表守卫 |

---

## 八、运行方式

```bash
# 1. 安装依赖
pip install langchain langchain-openai langchain-chroma langchain-community \
            langchain-text-splitters langgraph python-dotenv pyyaml

# 2. 配置 .env（API Key）

# 3. 首次运行：加载知识库
python -m rag.vector_store

# 4. 启动 Agent
python -m agent.react_agent
```

---

## 九、扩展方向

1. **真实工具接入**：替换 `get_weather`、`get_user_id` 等模拟工具为真实 API
2. **流式输出优化**：Agent 回答支持 SSE 流式推送
3. **多轮对话记忆**：引入对话摘要或滑动窗口记忆
4. **知识库增量更新**：定时扫描 data/ 目录自动更新向量库
5. **模型降级策略**：超时自动切换 `qwen-max` → `qwen-turbo`
6. **前端集成**：接入 Web/小程序前端
