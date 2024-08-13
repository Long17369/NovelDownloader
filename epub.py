"""下载书籍转换为EPUB 
Version : 1.0.0.00
Date : 2024/08/13 15:00
Author : Long17369
"""


import json
import os
from typing import Any, Dict, Union
import requests
from ebooklib import epub


class Main():
    def __init__(self) -> None:
        self.book = epub.EpubBook()
        self.info: Dict[str, Any] = {}

    def load_progress(self):
        """
        加载进度信息。

        尝试从指定的进度文件中加载进度信息，如果文件不存在或格式不正确，则初始化进度信息。
        这个方法主要用于恢复程序中断前的下载进度，以便继续未完成的工作。
        """
        # 尝试打开进度文件并加载进度信息
        try:
            # 尝试打开进度文件，并加载其中的进度信息
            with open('./txt/progress_file.json', 'r', encoding='utf-8') as f:
                # 从JSON文件中加载进度信息
                progress: Dict[str, Dict[Union[str, int], Union[str, int]]] = json.load(f)[
                    self.info['name']]
                # 更新信息字典中的进度信息
                self.info['progress'] = progress
        # 如果进度文件不存在，捕获异常并初始化进度信息
        except FileNotFoundError:
            # 如果进度文件不存在，初始化进度信息
            print('进度文件不存在，正在创建新进度文件')
            self.info['progress'] = {'Chapter_size': {}}
        # 如果进度文件格式不正确，捕获异常并初始化进度信息
        except json.JSONDecodeError:
            # 如果进度文件存在但格式不正确，删除文件
            print('进度文件格式不正确，正在删除旧进度文件')
            os.remove('./txt/progress_file.json')
            # 初始化进度信息
            self.info['progress'] = {'Chapter_size': {}}
        # 如果进度文件中不包含所需的名字，捕获异常并初始化进度信息
        except KeyError:
            # 如果进度文件中的数据不包含所需的名字，重新下载
            print('进度文件中不包含本小说，请重新下载')

    def setinfo(self) -> None:
        self.book.set_title(self.info['title'])
        try:
            self.book.add_author(self.info['author'])
        except:
            self.book.add_author(self.info['novel:author'])
        for i in self.info:
            if i in ['title', 'author', "name", 'progress']:
                continue
            if 'novel:' in i:
                self.book.add_metadata(
                    'DC', i.replace('novel:', ''), self.info[i])
            else:
                self.book.add_metadata('DC', i, self.info[i])
        try:
            if 'ethxs' in self.info['url']:
                res = requests.get(f'm.ethxs.com/{self.info["image"]}')
                if res.status_code == 200:
                    self.book.set_cover('cover.jpg', res.content)
        except:
            if 'rhmm18' in self.info["novel:url"]:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.37'}
                res = requests.get(f'{self.info["image"]}', headers=headers)
                if res.status_code == 200:
                    self.book.set_cover('cover.jpg', res.content)

    def add_chapter(self, Chapter: int) -> None:
        title = ''
        text = ''
        with open(f'./txt/Cache/{self.info["name"]}/{Chapter}', 'r', encoding='utf-8') as f:
            title = f.readline().replace(f'第{Chapter}章 ', '')
            text = f.read()
        self.book.add_item(epub.EpubHtml(
            title=title, file_name=f'{Chapter}.xhtml', content=text))

    def main(self, name):
        self.info['name'] = name
        self.load_progress()
        self.info.update(self.info['progress']['info'])
        self.setinfo()
        for i in range(1, len(self.info['progress']['Chapter_size'])):
            if os.path.getsize(f'./txt/Cache/{self.info["title"]}/{i}') != self.info['progress']['Chapter_size'][str(i)]:
                print(f'存在章节缓存问题，请重新下载\n{i}')
                # return False
            self.add_chapter(i)
        epub.write_epub(
            './txt/'+self.info['name']+'.epub', self.book, {'compression': 2, })
