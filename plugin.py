import time
<<<<<<< HEAD
from typing import List, Tuple, Type
from openai import OpenAI
=======
import asyncio
from typing import List, Tuple, Type
from openai import AsyncOpenAI  # 改为异步客户端
from tenacity import retry, stop_after_attempt, wait_exponential  # 重试机制
>>>>>>> ca17caa (异步化处理，配置更新)
from src.common.logger import get_logger
from src.plugin_system import (
    BasePlugin,
    register_plugin,
    BaseTool,
    ComponentInfo,
    ConfigField,
    ToolParamType,
<<<<<<< HEAD
=======
    message_api
>>>>>>> ca17caa (异步化处理，配置更新)
)

logger = get_logger("internet_search_plugin")

<<<<<<< HEAD

class SearchOnlineTool(BaseTool):
    """在线搜索工具 - 用于搜索互联网上的信息"""

=======
class SearchOnlineTool(BaseTool):
    """在线搜索工具 - 用于搜索互联网上的信息"""
    
    # 类属性，用于并发控制
    _semaphore = None
    
>>>>>>> ca17caa (异步化处理，配置更新)
    name = "search_online"
    description = "在互联网上搜索信息，当你有难以理解的，有时效性的，或难以确定的内容时，可以使用此工具进行搜索。"
    parameters = [
        ("question", ToolParamType.STRING, "要查询的关键词或问题", True, None)
    ]
    available_for_llm = True

    async def execute(self, function_args) -> dict[str, str]:
        """执行知识搜索"""
        try:
            query = function_args.get("question")  
            search_results = await self._search_knowledge(query) # 执行搜索逻辑   
            result = self._format_search_results(query, search_results) # 格式化结果
            return {"name": self.name, "content": result}
        except Exception as e:
            return {"name": self.name, "content": f"知识搜索失败: {str(e)}"}

    async def direct_execute(self, **function_args) -> str:
        '''
        直接调用联网搜索工具

        Args:
            question: 要进行搜索的问题或关键词

        Return:
            result: 模型返回的结果
        '''
<<<<<<< HEAD
        if self.parameters and (
            missing := [p for p in self.parameters.get("required", []) if p not in function_args]
        ):
            raise ValueError(
                f"工具类 {self.__class__.__name__} 缺少必要参数: {', '.join(missing)}"
            )
=======
        # 修正参数检查逻辑
        required_params = [p[0] for p in self.parameters if p[3]]  # 提取必填参数名
        missing = [p for p in required_params if p not in function_args]
        if missing:
            raise ValueError(f"工具类 {self.__class__.__name__} 缺少必要参数: {', '.join(missing)}")
        
>>>>>>> ca17caa (异步化处理，配置更新)
        try:
            query = function_args.get("question")
            # 执行搜索逻辑
            search_results = await self._search_knowledge(query)
            return search_results.get("content", "")
        except Exception as e:
            logger.warning(f"执行搜索时发生异常: {e}")
            return ""

<<<<<<< HEAD
    async def _search_knowledge(self, query: str) -> list:
        """执行知识搜索"""
        logger.info(f"正在执行搜索，搜索内容：{query}")
        client = OpenAI(
            base_url=self.get_config("model.base_url"),
            api_key=self.get_config("model.api_key"),
        )
        try:
            completion = client.chat.completions.create(
=======
    async def _search_knowledge(self, query: str) -> dict:
        """执行知识搜索"""
        # 延迟初始化信号量
        if self._semaphore is None:
            max_concurrency = self.get_config('search.max_concurrency', 5)
            self._semaphore = asyncio.Semaphore(max_concurrency)
        
        # 获取重试配置
        retry_attempts = self.get_config('search.retry_attempts', 3)
        retry_wait_min = self.get_config('search.retry_wait_min', 2.0)
        retry_wait_max = self.get_config('search.retry_wait_max', 10.0)
        timeout = self.get_config('search.timeout', 20.0)
        
        # 使用重试机制
        for attempt in range(1, retry_attempts + 1):
            try:
                async with self._semaphore:
                    return await self._execute_search(query, timeout)
            except (asyncio.TimeoutError, Exception) as e:
                if attempt < retry_attempts:
                    # 指数退避算法
                    wait_time = min(retry_wait_min * (2 ** (attempt - 1)), retry_wait_max)
                    logger.warning(f"搜索失败({attempt}/{retry_attempts})，等待{wait_time:.1f}秒后重试: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    if isinstance(e, asyncio.TimeoutError):
                        return {"content": "搜索请求超时，请稍后再试"}
                    else:
                        return {"content": "搜索服务暂时不可用"}

    async def _execute_search(self, query: str, timeout: float) -> dict:
        """执行搜索的核心逻辑"""
        logger.info(f"正在执行搜索，搜索内容：{query}")
        content = f"""
你是一名专业的网络搜索专家，可以根据以下的要求精准的汇总出用户需要的信息，且一定能够保证信息的真实性和可靠性，汇总信息时不会带有个人主观色彩。
<doc>
这一段将详细为你说明所有内容块的用途，以及你如何通过他们精准的理解需求以优化你的回复。
<doc>：
该内容块是对提示文本规范化的解释说明，帮助你理解后文每个内容块的用处和解释。
<command>:
该内容块是对总体命令要求的阐述，也是你务必要严格遵守的内容。
<direction>:
该内容块包含对所需返回信息的方向的总体赘述。你需要根据该内容块中的内容调整你总结信息的方向。请注意，并不是所有的问题都一定完全契合该内容块中描述的方向。你应该根据自己的判断调整最后的输出内容，而不是完全死板的遵守该内容块中的内容。
<question>：
该内容块是你需要进行检索的核心问题或关键词。你最终输出的内容一定是围绕该内容块中的内容进行的，且尽量减少一切与该内容块中的内容无关的信息。
<context>：
该内容块包含一些必要的历史聊天信息。有时请求的question中指向性不明确，这时需要你通过提供的历史聊天信息来猜测出用户提出问题的具体内容。
<time>:
该内容块包含当前的详细的时间信息，帮助你选取更具有时效性的内容。
</doc>

<command>
请根据<question>和<context>中的内容，在网络上搜索相关内容，同时注意：
1.你的参考来源应该是可信的，权威的；
2.你不应该输出任何带有主观色彩的内容；
3.如果搜索的问题在网络上尚无定论，你应该将不同观念一起汇总出来；
4.当涉及到国家政治等敏感内容时，请务必保持绝对客观中立的角度，必要时你可以拒绝输出回答，并提醒用户保持严肃性；
5.你输出的内容应当足够简洁精炼，不要长篇大论，但要保留基本信息；
6.如果你无法给出一个可信的回答，就不要回答，禁止胡乱编造；
7.尽量选用最新的消息来源。
</command>

<direction>
{self.get_config('search.direction','请着重考虑与ACG文化、网络热梗、游戏术语、近期热点内容相关的方面。')}
</direction>

<question>
{query}
</question>

<context>
{self.get_messages_before(self.get_config('search.time_gap',270),self.get_config('search.max_limit',10))}
</context>

<time>
{time.strftime('%Y-%m-%d %H:%M', time.localtime())}
</time>
"""
        client = AsyncOpenAI(
            base_url=self.get_config("model.base_url"),
            api_key=self.get_config("model.api_key"),
        )
        
        try:
            completion = await client.chat.completions.create(
>>>>>>> ca17caa (异步化处理，配置更新)
                model=self.get_config("model.model"),
                messages=[
                    {
                        "role": "system",
                        "content": "你是专业的网络搜索助手，擅长从互联网上获取最新信息",
                    },
                    {
                        "role": "user",
<<<<<<< HEAD
                        "content": f"现在是{time.strftime('%Y-%m-%d %H:%M', time.localtime())},一些爱打游戏、爱追番、爱刷抖音b站小红书的年轻人发来了一串消息，请在网络上搜索有关“{query}的内容”,只回答与{query}的方面，选用最新的消息来源，不要回答无关的信息",
                    },
                ],
                temperature=0.2,
            )
            return [
                {
                    "title": f"{query}的解释",
                    "content": completion.choices[0].message.content,
                }
            ]
        except Exception as e:
            logger.error(f"执行搜索时出现错误：{e}")
            return [
                {
                    "title": f"{query}的解释",
                    "content": "执行搜索失败",
                }
            ]


    def _format_search_results(self, query: str, results: list) -> str:
        """格式化搜索结果"""
        if not results:
            return f"未找到关于 '{query}' 的相关信息"

        formatted_text = f"📚 关于 '{query}' 的搜索结果:\n\n"

        for result in results:  # 限制显示前3条
            title = result.get("title", "无标题")
            content = result.get("content", "无摘要")

            formatted_text += f"**{title}**\n"
            formatted_text += f"   {content}\n"

        return formatted_text.strip()


# ===== 插件注册 =====


=======
                        "content": content,
                    },
                ],
                temperature=0.2,
                timeout=timeout  # 使用配置的超时时间
            )
            
            logger.debug(f"搜索完成: {query}")
            return {"content": completion.choices[0].message.content}
            
        except asyncio.TimeoutError:
            logger.warning(f"搜索超时: {query}")
            raise
        except Exception as e:
            logger.error(f"搜索失败: {query} - {str(e)}")
            raise


    def _format_search_results(self, query: str, result: dict) -> str:
        """格式化搜索结果"""
        if not result:
            return f"未找到关于 '{query}' 的相关信息"

        formatted_text = f"📚 关于 '{query}' 的搜索结果:\n\n"
        
        content = result.get("content", "无摘要")
        formatted_text += f"   {content}\n"

        return formatted_text.strip()

    def get_messages_before(self, time_gap: int = 270, limit: int = 10):
        current = time.time()
        earlier = current - time_gap
        messages = message_api.get_messages_by_time(earlier,current,limit=limit)
        return message_api.build_readable_messages_to_str(messages)
        
# ===== 插件注册 =====

>>>>>>> ca17caa (异步化处理，配置更新)
@register_plugin
class InternetSearchPlugin(BasePlugin):
    """InternetSearch插件 - 联网搜索插件"""

    # 插件基本信息
    plugin_name: str = "internet_search_plugin"  # 内部标识符
    enable_plugin: bool = True
    dependencies: List[str] = []  # 插件依赖列表
<<<<<<< HEAD
    python_dependencies: List[str] = []  # Python包依赖列表
=======
    python_dependencies: List[str] = ["openai", "tenacity"]  # 添加新依赖
>>>>>>> ca17caa (异步化处理，配置更新)
    config_file_name: str = "config.toml"  # 配置文件名

    # 配置节描述
    config_section_descriptions = {
        "plugin": "插件基本信息",
        "model": "大模型设置",
<<<<<<< HEAD
        "promt": "查询提示词",
=======
        "search": "搜索设置",
>>>>>>> ca17caa (异步化处理，配置更新)
    }

    # 配置Schema定义
    config_schema: dict = {
        "plugin": {
            "name": ConfigField(
                type=str, default="internet_search_plugin", description="插件名称"
            ),
<<<<<<< HEAD
            "version": ConfigField(type=str, default="1.0.0", description="插件版本"),
=======
            "version": ConfigField(type=str, default="1.1.0", description="插件版本"),
            "config_version": ConfigField(type=str, default="1.2.0", description="配置文件版本"),
>>>>>>> ca17caa (异步化处理，配置更新)
            "enabled": ConfigField(
                type=bool, default=False, description="是否启用插件"
            ),
        },
        "model": {
            "base_url": ConfigField(
                type=str,
                default="https://rinkoai.com/v1",
                description="模型API基础URL",
            ),
            "api_key": ConfigField(
<<<<<<< HEAD
                type=bool, default="xxxxxxxxxxxxxxxxx", description="你的API Key"
            ),
            "model": ConfigField(type=str, default="gpt-4.1-search", description="使用的模型名称"),
        },
=======
                type=str, default="", description="你的API Key（建议通过环境变量设置）"
            ),
            "model": ConfigField(type=str, default="gpt-4.1-search", description="使用的模型名称"),
        },
        "search":{
            "direction": ConfigField(
                type=str,
                default="请着重考虑与ACG文化、网络热梗、游戏术语、近期热点内容相关的方面。",
                description="描述模型应当着重考虑的搜索方向",
            ),
            "time_gap": ConfigField(
                type=int,
                default=270,
                description="提供最近多长时间内的聊天记录（秒）",
            ),
            "max_limit": ConfigField(
                type=int,
                default=10,
                description="提供最多多少条聊天记录（0为不限制）",
            ),
            # === 新增配置项 ===
            "timeout": ConfigField(
                type=float,
                default=20.0,
                description="API调用超时时间（秒）",
            ),
            "max_concurrency": ConfigField(
                type=int,
                default=5,
                description="最大并发搜索请求数",
            ),
            "retry_attempts": ConfigField(
                type=int,
                default=3,
                description="搜索失败时的重试次数",
            ),
            "retry_wait_min": ConfigField(
                type=float,
                default=2.0,
                description="重试之间的最小等待时间（秒）",
            ),
            "retry_wait_max": ConfigField(
                type=float,
                default=10.0,
                description="重试之间的最大等待时间（秒）",
            ),
            # ================
        }
>>>>>>> ca17caa (异步化处理，配置更新)
    }

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        return [
            (SearchOnlineTool.get_tool_info(), SearchOnlineTool),
        ]
