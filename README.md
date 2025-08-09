# Internet Search Plugin

一个基于大语言模型的智能联网搜索插件，能够实时获取互联网上的最新信息。

## 功能特性

- 🔍 **智能搜索**: 基于大语言模型的智能搜索，理解用户意图
- 🌐 **实时信息**: 获取最新的网络信息和时效性内容
- 🎯 **精准匹配**: 只返回与查询相关的信息，过滤无关内容
- 🔧 **灵活配置**: 支持自定义API配置和模型选择
- 📱 **年轻化**: 针对游戏、动漫、社交媒体等年轻人关注的内容优化

## 安装要求

### Python依赖
```bash
pip install openai
```

### 系统依赖
- Python 3.7+
- 支持异步操作的环境

## 配置说明

插件使用 `config.toml` 配置文件，包含以下配置项：

### 插件基本配置
```toml
[plugin]
name = "internet_search_plugin"
version = "1.0.0"
enabled = false  # 设置为 true 启用插件
```

### 模型配置
```toml
[model]
base_url = "https://rinkoai.com/v1"  # API基础URL~~（@rinkoai这不给点广告费）~~
api_key = "your_api_key_here"        # 你的API密钥
model = "gpt-4.1-search"             # 使用的模型名称
```

## 使用方法

### 1. 作为LLM工具调用

插件会自动注册为LLM可用的工具，当LLM需要搜索信息时会自动调用：

```python
# LLM会在需要时自动调用搜索工具
# 工具名称: search_online
# 参数: question (必需) - 要搜索的关键词或问题
```

### 2. 直接调用

本插件支持外部插件调用search_online工具进行联网搜索，并对直接调用的场景返回结果进行了优化

```python
from src.plugin_system.apis import tool_api

# 获取工具实例
search_tool = tool_api.get_tool_instance("search_tool")

# 直接调用搜索
result = await search_tool.direct_execute(question="最新的AI技术发展")
print(result)
```


## 工具参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| question | string | 是 | 要查询的关键词或问题 |

## 返回格式

### execute方法返回
```python
{
    "name": "search_online",
    "content": "📚 关于 '查询内容' 的搜索结果:\n\n**标题**\n   搜索结果内容..."
}
```

### direct_execute方法返回
```python
"搜索结果的纯文本内容"
```

## 使用场景

- ✅ 查询最新新闻和时事
- ✅ 了解游戏、动漫最新资讯  
- ✅ 搜索社交媒体热点话题
- ✅ 获取技术发展动态
- ✅ 查找难以理解的概念解释

## 注意事项

1. **API配置**: 确保配置了有效的API密钥和正确的base_url
2. **网络连接**: 需要稳定的网络连接访问API服务
3. **费用控制**: 每次搜索会消耗API调用次数，注意控制使用频率
4. **内容过滤**: 插件会自动过滤无关信息，只返回与查询相关的内容

## 错误处理

插件包含完善的错误处理机制：
- API调用失败时返回友好的错误信息
- 网络异常时提供降级处理
- 参数缺失时给出明确的错误提示

## 日志记录

插件使用统一的日志系统记录：
- 搜索请求和结果
- 错误和异常信息
- 性能和调用统计

## 开发者信息

- **插件类型**: BasePlugin
- **工具类型**: BaseTool  
- **支持异步**: ✅
- **LLM集成**: ✅

## 版本历史

- **v1.0.0**: 初始版本，支持基本的联网搜索功能