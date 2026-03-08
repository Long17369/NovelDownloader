"""
core.download 的 Docstring
"""

from asyncio import gather, create_task

from .base import BasePlugin, ChapterInfo
from .logger import get_logger


logger = get_logger(__name__)


class Download:
    async def download_novel(
        self,
        plugin_list: list[tuple[int, BasePlugin]],
        url: str | list[str],
        check_support: bool = True,
    ):
        """下载小说"""
        try:
            if isinstance(url, list):
                for u in url:
                    create_task(self.download_novel(plugin_list, u, check_support))
                return

            if check_support:
                has_support, plugin = await self.select_supported_plugin(plugin_list, url)
            else:
                logger.info("暂时不支持关闭插件支持检查")
                return

            if not has_support or not plugin:
                return

            logger.info(f"使用 {plugin.name} 下载 {url}")
            logger.info("正在获取小说信息...")
            novel_info = await plugin.get_novel_info(url)
            logger.info(
                f"获取小说信息完毕:\n小说标题:{novel_info.title}\n小说作者:{novel_info.author}\n小说封面链接:{novel_info.cover_url}"
            )

            logger.info("正在下载小说章节...")

            chapter_info: list[ChapterInfo] = []
            for chapter_url in novel_info.chapter_urls:
                if isinstance(chapter_url, list):
                    chapter_info.extend(await gather(*[plugin.download(u) for u in chapter_url]))
                else:
                    chapter_info.append(await plugin.download(chapter_url))

            logger.info("下载小说章节完毕")
        except Exception as e:
            logger.error(f"下载小说失败: {e}")

    async def download_novel_chapter(self, url: str): ...

    async def select_supported_plugin(
        self, plugin_list: list[tuple[int, BasePlugin]], url: str
    ) -> tuple[bool, BasePlugin | None]:
        """
        为给定的 URL 从插件列表中选择一个支持的插件。

        行为:
        - 遍历 `plugin_list`（格式: list[tuple[int, BasePlugin]]），每项为 `(priority, plugin)`。
        - 当插件的 `suport(url)` 返回 True 时，会将该插件加入候选列表。
        - 函数假定 `plugin_list` 已按 `priority` 从高到低排序；一旦遇到比当前最高优先级更低的优先级，遍历会停止，
            因此只会收集具有最高优先级的一组插件（可能是一个或多个）。
        - 如果没有找到支持的插件，返回 `(False, None)`。
        - 如果找到多个同等优先级的插件，会在控制台列出供用户选择（通过 `input()` 输入编号）。无效输入时自动选择第一个。
        - 如果只找到一个插件，直接返回该插件。

        参数:
        - plugin_list (list[tuple[int, BasePlugin]]): 插件及其优先级的列表，优先级越大表示优先级越高。
        - url (str): 需要下载的小说页面或章节的 URL。

        返回:
        - tuple[bool, BasePlugin | None]: (是否找到支持插件, 选中的插件实例或 None)。

        注意:
        - 本函数会打印提示并使用 `input()` 进行交互，因而不适合在无交互的环境（如后台任务、自动化脚本）中使用。
        - 插件需实现 `suport(url)` 方法以判断是否支持给定 URL，并且应提供 `name` 属性用于显示。
        """
        supported_plugins: list[BasePlugin] = []

        _priority = -1

        for priority, plugin in plugin_list:
            if await plugin.suport(url):
                if priority < _priority:
                    break
                supported_plugins.append(plugin)
                _priority = priority

        if not supported_plugins:
            logger.info(f"没有找到支持下载 {url} 的插件")
            return False, None

        if len(supported_plugins) > 1:
            logger.info(f"找到多个支持下载 {url} 的插件,请选择一个插件进行下载:")
            for i, plugin in enumerate(supported_plugins):
                logger.info(f"[{i}] {plugin.name}")
            num = input("请输入插件编号:")

            try:
                num = int(num)
                if num < 0 or num >= len(supported_plugins):
                    logger.info("输入的插件编号无效, 自动选择第一个插件")
                    return True, supported_plugins[0]
                plugin = supported_plugins[num]
            except ValueError:
                logger.info("输入的插件编号无效, 自动选择第一个插件")
                return True, supported_plugins[0]

            return True, supported_plugins[num]

        plugin = supported_plugins[0]
        return True, plugin
