import time
from typing import List, Tuple, Type
from openai import OpenAI
from src.common.logger import get_logger
from src.plugin_system import (
    BasePlugin,
    register_plugin,
    BaseTool,
    ComponentInfo,
    ConfigField,
    ToolParamType,
)

logger = get_logger("internet_search_plugin")


class SearchOnlineTool(BaseTool):
    """在线搜索工具 - 用于搜索互联网上的信息"""

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
        if self.parameters and (
            missing := [p for p in self.parameters.get("required", []) if p not in function_args]
        ):
            raise ValueError(
                f"工具类 {self.__class__.__name__} 缺少必要参数: {', '.join(missing)}"
            )
        try:
            query = function_args.get("question")
            # 执行搜索逻辑
            search_results = await self._search_knowledge(query)
            return search_results.get("content", "")
        except Exception as e:
            logger.warning(f"执行搜索时发生异常: {e}")
            return ""

    async def _search_knowledge(self, query: str) -> list:
        """执行知识搜索"""
        logger.info(f"正在执行搜索，搜索内容：{query}")
        client = OpenAI(
            base_url=self.get_config("model.base_url"),
            api_key=self.get_config("model.api_key"),
        )
        try:
            completion = client.chat.completions.create(
                model=self.get_config("model.model"),
                messages=[
                    {
                        "role": "system",
                        "content": "你是专业的网络搜索助手，擅长从互联网上获取最新信息",
                    },
                    {
                        "role": "user",
                        "content": f"现在是{time.strftime("%Y-%m-%d %H:%M", time.localtime())},一些爱打游戏、爱追番、爱刷抖音b站小红书的年轻人发来了一串消息，请在网络上搜索有关“{query}的内容”,只回答与{query}的方面，选用最新的消息来源，不要回答无关的信息",
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


@register_plugin
class InternetSearchPlugin(BasePlugin):
    """InternetSearch插件 - 联网搜索插件"""

    # 插件基本信息
    plugin_name: str = "internet_search_plugin"  # 内部标识符
    enable_plugin: bool = True
    dependencies: List[str] = []  # 插件依赖列表
    python_dependencies: List[str] = []  # Python包依赖列表
    config_file_name: str = "config.toml"  # 配置文件名

    # 配置节描述
    config_section_descriptions = {
        "plugin": "插件基本信息",
        "model": "大模型设置",
        "promt": "查询提示词",
    }

    # 配置Schema定义
    config_schema: dict = {
        "plugin": {
            "name": ConfigField(
                type=str, default="internet_search_plugin", description="插件名称"
            ),
            "version": ConfigField(type=str, default="1.0.0", description="插件版本"),
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
                type=bool, default="xxxxxxxxxxxxxxxxx", description="你的API Key"
            ),
            "model": ConfigField(type=str, default="gpt-4.1-search", description="使用的模型名称"),
        },
    }

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        return [
            (SearchOnlineTool.get_tool_info(), SearchOnlineTool),
        ]
