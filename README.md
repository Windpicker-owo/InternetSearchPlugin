# 🔍 Internet Search Plugin 文档

*智能联网搜索插件，助你获取最新最准确的信息*

## 🌟 核心功能

```markdown
✅ **智能联网搜索**  
- 通过自然语言查询获取最新网络信息
- 特别优化对ACG文化、网络热梗、游戏术语的识别
- 支持时效性内容搜索（自动获取当前时间）

🛠️ **强大工具特性**  
- 自动重试机制（最多3次）
- 智能并发控制（默认5并发）
- 超时自动处理（默认20秒）
- 上下文感知搜索（自动关联近期聊天记录）

⚙️ **高度可配置**  
- 11个可调整参数满足不同需求
- 支持自定义搜索方向
- 灵活控制历史记录范围
```

## 📦 安装与启用

### 依赖安装

通常情况下会自动安装以下依赖。如果无法正常自动安装，请手动安装：

```bash
pip install openai tenacity
```

### 配置文件 (`config.toml`)
```toml
[plugin]
name = "internet_search_plugin"
version = "1.1.0"
enabled = true  # 启用插件

[model]
base_url = "https://rinkoai.com/v1"  # API基础地址
api_key = "your-api-key-here"        # 你的API密钥
model = "gpt-4.1-search"             # 使用的模型

[search]
direction = "请着重考虑与ACG文化、网络热梗、游戏术语、近期热点内容相关的方面。"
time_gap = 270       # 关联的聊天记录时间范围（秒）
max_limit = 10       # 关联的最大聊天记录条数
timeout = 20.0       # API超时时间（秒）
max_concurrency = 5  # 最大并发数
retry_attempts = 3   # 重试次数
retry_wait_min = 2.0 # 最小重试等待时间
retry_wait_max = 10.0# 最大重试等待时间
```

## 🚀 使用方法

### 1. 直接调用工具
```python
from src.plugin_system.apis import tool_api

search_tool = tool_api.get_tool_instance("search_tool")

result = await search_tool.direct_execute(
    question="EVA终章上映时间"
)
```

### 2. 自然语言触发
```
用户：最近有什么好玩的独立游戏推荐？
AI: 🤖 [自动触发search_online]...
```

## ⚙️ 配置详解

### 模型设置 (`[model]`)
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `base_url` | str | `https://rinkoai.com/v1` | API基础地址 |
| `api_key` | str | 空 | 认证密钥 |
| `model` | str | `gpt-4.1-search` | 使用的模型名称 |

### 搜索设置 (`[search]`)
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `direction` | str | ACG文化相关提示 | 搜索结果偏好方向 |
| `time_gap` | int | 270 | 关联聊天记录时间范围(秒) |
| `max_limit` | int | 10 | 最大关联消息数 |
| `timeout` | float | 20.0 | 请求超时时间(秒) |
| `max_concurrency` | int | 5 | 最大并发请求数 |
| `retry_attempts` | int | 3 | 失败重试次数 |
| `retry_wait_min` | float | 2.0 | 最小重试间隔(秒) |
| `retry_wait_max` | float | 10.0 | 最大重试间隔(秒) |

## 📝 使用示例

```markdown
用户：赛博朋克2077最新DLC什么时候发布？

🔍 插件行为：
1. 自动提取关键词 "赛博朋克2077 DLC发布时间"
2. 搜索最新官方信息
3. 关联近期游戏讨论记录
4. 返回结构化结果

💬 返回结果：
📚 关于 '赛博朋克2077最新DLC' 的搜索结果：

根据CD Projekt Red官方消息，《赛博朋克2077》全新DLC"往日之影"
将于2023年9月26日正式发布，登陆PC/PS5/Xbox Series平台...
```

## ⚠️ 注意事项

1. **API密钥安全**  
   ```diff
   + 正确：将api_key存储在配置文件中
   - 错误：在代码中硬编码api_key
   ```

2. **网络要求**  
   - 确保服务器可访问配置的`base_url`
   - 建议网络延迟 < 200ms

3. **资源消耗**  
   ```python
   # 根据服务器性能调整：
   max_concurrency = 3  # 低配服务器
   timeout = 30.0       # 慢速网络环境
   ```

4. **内容审核**  
   - 插件自动过滤敏感内容
   - 遇到政治等敏感话题会自动拒绝回答

---

> 💡 **使用提示**：当需要**时效性信息**、**特定领域知识**或**术语解释**时，此工具效果最佳！