from abc import ABC
from pydantic import BaseModel, Field


class NovelInfo(BaseModel):
    title: str = Field(default="")  # 小说标题
    author: str = Field(default="")  # 小说作者
    cover_url: str = Field(default="")  # 小说封面链接
    chapter_urls: list[str | list[str]] = Field(
        default_factory=list[str | list[str]]
    )  # 章节链接列表


class ChapterInfo(BaseModel):
    title: str = Field(default="")  # 章节标题
    url: str = Field(default="")  # 章节链接
    content: str = Field(default="")  # 章节内容


class BasePlugin(ABC):
    name:str
    priority:int

    def __init_subclass__(cls) -> None:
        plugin_list.append(cls)
        if not hasattr(cls, "name"):
            cls.name = cls.__name__
        return super().__init_subclass__()

    async def suport(self, url: str) -> bool:
        """判断是否支持下载该链接"""
        return False

    async def get_novel_info(self, url: str) -> NovelInfo:
        """获取小说信息"""
        return NovelInfo()

    async def download(self, url: str | list[str]) -> ChapterInfo:
        """下载链接并返回文件路径"""
        return ChapterInfo()


plugin_list: list[type[BasePlugin]] = []
