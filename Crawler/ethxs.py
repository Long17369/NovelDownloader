"""获取ethxs.com(以太小说网的小说)
Version : 2.0.0.00
Date : 2024/10/16
Author : Long17369
"""


import base64
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, _base, thread
from typing import Any, Dict, List, Union

import bs4
import requests


class Main():
    """
    重构后的爬虫代码
    """

    def __init__(self) -> None:
        """
        初始化爬虫类的属性。

        初始化包括定义用于编码和解码的字典结构，设置线程池执行器等。
        """
        # 定义一个字典，用于存储待解码文本，键为整数，值为另一个字典，该字典的键为整数，值为字符串列表。
        self.code: Dict[int, Dict[int, List[str]]] = {}
        # 定义一个字典，用于存储解码后的结果，键可以是任意类型，值为字符串。
        self.decoded: Dict[Any, str] = {}
        # 定义一个通用信息字典，用于存储各种相关信息。
        self.info: Dict[str, Any] = {}
        # 定义一个字典，用于存储线程池执行器实例
        self.executor_crawl: Dict[str, thread.ThreadPoolExecutor] = {}
        # 定义一个字典，用于存储线程池执行器的任务结果
        self.executor_results: Dict[str, List[_base.Future]] = {}
        # 定义一个字典，用于存储被删除的章节信息
        self.deleted: Dict[int, List[str]] = {}
        # 定义一个布尔值，用于指示是否使用代理（请自行使用）
        self.use_proxy = False
        # 定义一个字典，用于存储代理信息（请自行使用）
        self.proxies = {
            'http': '',
            'https': ''
        }
        self.error: Dict[int, _base.Future] = {}

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
            # 如果进度文件中的数据不包含所需的名字，初始化进度信息
            print('进度文件中不包含本小说，正在添加新的进度')
            self.info['progress'] = {'Chapter_size': {}}

    def save_progress(self):
        """
        保存进度信息到JSON文件。

        尝试读取并更新现有进度文件，如果文件不存在或格式不正确，则创建新文件。
        使用UTF-8编码，并以可读的格式写入JSON数据。

        解决方案:
        - 如果文件存在但格式不正确，则删除文件并重新创建。
        - 如果文件不存在，则直接创建新文件。
        """
        try:
            # 尝试打开并读取进度文件
            with open('./txt/progress_file.json', 'r+', encoding='utf-8') as f:
                data = json.load(f)
                # 更新数据字典中当前进度的信息
                data[self.info['name']] = self.info['progress']
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=4)
        except json.JSONDecodeError:
            # 如果文件格式不正确，删除文件并递归调用自身重新尝试
            os.remove('./txt/progress_file.json')
            return self.save_progress()
        except FileNotFoundError:
            # 如果文件不存在，创建新文件并写入当前进度信息
            with open('./txt/progress_file.json', 'w', encoding='utf-8') as f:
                data = {self.info['name']: self.info['progress']}
                json.dump(data, f, ensure_ascii=False, indent=4)

    def crawler(self, chapter_num: int, href: List[str]):
        """
        爬虫函数，用于下载指定小说的指定章节。

        参数:
        chapter_num: int - 需要下载的章节编号
        href: List[str] - 小说的URL列表，其中href[0]是小说主页的URL，href[1]是小说目录的URL
        """
        # 检查章节是否已经下载过，如果已经下载并且与缓存文件大小相同，则不再下载
        if str(chapter_num) in (self.info['progress']['Chapter_size']):
            if os.path.getsize(f'./txt/Cache/{self.info["title"]}/{chapter_num}') == self.info['progress']['Chapter_size'][str(chapter_num)]:
                return
        # 输出开始下载的提示信息
        print(f'开始下载第{chapter_num}章')
        page = 0
        self.code[chapter_num] = {}
        # 开始循环下载页面，直到无法获取页面为止
        while page >= 0:
            # 对于第一页，使用小说主页的URL；对于后续页面，构造相应的URL
            if page == 0:
                # 构造小说第一章的URL
                page_url = "http://m.ethxs.com/" + href[0]
            else:
                # 构造后续章节的URL
                page_url = "http://m.ethxs.com/" + \
                    href[0].split(".html")[0] + '_' + str(page) + ".html"
            # 尝试获取页面，如果成功，则继续获取下一页；如果失败，则结束循环
            if self.get_page(page_url, chapter_num, page):
                # 如果成功获取到页面，尝试获取下一页
                page += 1
            else:
                # 如果无法获取到页面，结束爬取
                page = -1
        if self.code[chapter_num] == {}:
            print(f'第{chapter_num}章下载失败')
            return
        # 解码下载的章节内容
        self.decode(chapter=chapter_num)
        # 将解码后的章节写入文件
        self.write(chapter_num, href[1])

    def get_page(self, url, chapter: int, page: int, error: int = 0) -> bool:
        """
        从给定的URL获取小说的指定章节和页面。

        参数:
        url (str): 小说章节页面的URL。
        chapter (int): 章节的编号。
        page (int): 页面的编号。
        error (int): 当前的错误计数，用于重试机制，默认为0。

        返回:
        bool: 如果成功获取页面，则返回True；否则返回False。
        """
        # 尝试发送HTTP请求获取页面
        try:
            if self.use_proxy:
                respond = requests.get(
                    url, allow_redirects=False, proxies=self.proxies)
            else:
                respond = requests.get(url, allow_redirects=False)
        except:
            # 如果请求失败，根据错误计数决定是否重试
            if error < 5:
                time.sleep(5)  # 等待5秒后重试
                return self.get_page(url, chapter, page, error+1)
            else:
                print(f"第{chapter}章第{page}下载失败")
                self.code[chapter][page] = ['']
                return False
        else:
            # 如果请求重定向，视为完成本章下载
            if respond.status_code == 301:
                return False
            # 从响应中提取HTML内容
            html = respond.text
            # 提取正文中的密文
            code = self.extract_texts_from_html(html)
            # 删除HTML，减少资源占用
            del html
            # 将处理得到的密文写入self.code中
            self.code[chapter][page] = code
            return True

    def extract_texts_from_html(self, html_string):
        """
        提取HTML字符串中所有id为'txt'的<script>标签内的文本内容。
        返回一个列表，其中包含所有找到的文本内容。如果找不到指定的元素，
        则返回空列表。
        """
        texts: List[str] = []
        try:
            # 使用BeautifulSoup解析HTML，指定解析器为html.parser
            soup = bs4.BeautifulSoup(html_string, 'html.parser')

            # 查找所有id为'txt'的<script>标签
            script_tags: bs4.element.ResultSet[bs4.element.BeautifulSoup]
            script_tags = soup.find_all('div', id='txt')
            script_tag = script_tags[0].find_all('script')

            # 遍历所有找到的<script>标签，收集其文本内容
            texts = [h for i in script_tag for j,
                     h in enumerate(str(i).split("'")) if j == 1]

        except Exception as e:
            # 解析出错时，记录日志或进行其他错误处理
            print(f"Error occurred while parsing the HTML: {e}")
        return texts

    def decode(self, chapter: int = -1, code: str = '') -> None:
        """
        解码指定章节或代码。

        如果chapter参数为-1且code参数不为空，则认为是解码字符串。
        如果chapter参数不为-1且code参数为空，则认为是解码指定章节。

        参数:
        chapter: int，指定要解码的章节编号，默认为-1，表示解码字符串。
        code: str，待解码的字符串，默认为空

        返回:
        None，但会更新self.decoded
        """
        # 当章节参数为默认值-1且code不为空时，解码字符串
        if chapter == -1 and code != '':
            # 使用base64解码小说正文，并将结果存储在decoded字典中
            self.decoded['decode'] = base64.b64decode(code).decode('utf-8')
        # 当章节参数不为默认值且code为默认值空时，解码指定章节
        elif chapter != -1 and code == '':
            # 获取指定章节的解码信息
            decode_data = self.code[chapter]
            decoded_parts: List[str] = []
            # 初始化一个布尔值，用于判断是否需要删除
            delete = False
            # 遍历解码信息中的每个部分，进行解码
            for i in decode_data:
                for j in decode_data[i]:
                    # 使用base64解码每个部分
                    decoded = base64.b64decode(j).decode('utf-8')
                    # 去除开头和结尾的<p>和</p>标签
                    if decoded[:3:] == '<p>':
                        decoded = decoded[3::]
                    if decoded[-4::] == '</p>':
                        decoded = decoded[:-4:]
                    # 判断是否需要删除
                    if decoded[:3:] == 'div':
                        delete = not delete
                        if delete:
                            decoded = decoded[3::]
                    # 如果需要删除，则将解码后的部分添加到已删除列表中
                    if delete:
                        if not chapter in self.deleted:
                            self.deleted[chapter] = []
                        self.deleted[chapter].append(decoded)
                    else:
                        # 将解码后的部分添加到列表中
                        decoded_parts.append(decoded)
            # 将解码后的部分合并成字符串，以换行符分隔，并存储在decoded字典的对应章节中
            self.decoded[chapter] = '\n'.join(
                decoded_parts).replace('<p>—</p>', '\n')
            # 删除已解码的code
            del self.code[chapter]

    def write(self, chapter: int, chapter_name):
        """
        将章节名称和内容写入到指定章节的文本文件中。

        参数:
        chapter: int, 章节的编号，用于生成文件名和作为字典的键。
        chapter_name: str, 章节的名称，将写入文件作为章节标题。
        """
        # 判断文件是否存在
        if os.path.exists(f'./txt/Cache/{self.info["title"]}/{chapter}'):
            # 如果存在就删除文件
            os.remove(f'./txt/Cache/{self.info["title"]}/{chapter}')
        # 使用with语句确保文件正确打开和关闭，以utf-8编码写入
        with open(f'./txt/Cache/{self.info["title"]}/{chapter}', 'w', encoding='utf-8') as f:
            # 写入章节标题
            f.write(f'{chapter_name}\n')
            # 写入章节内容
            f.write(self.decoded[chapter])
        # 更新当前章节的进度信息(章节大小)
        self.info['progress']['Chapter_size'][str(chapter)] = os.path.getsize(
            f'./txt/Cache/{self.info["title"]}/{chapter}')
        # 从decoded字典中删除已处理的章节，减少资源占用
        del self.decoded[chapter]

    def write_all(self):
        """
        将所有章节内容合并写入到一个单独的文本文件中。

        本函数首先从缓存目录中读取每个章节的文本内容，然后将这些内容写入到一个名为
        标题.txt的文件中，每个章节之间用空行分隔。此外，它还会更新进度信息，将
        其余信息合并到进度信息中，并保存更新后的进度。
        """
        # 获取进度信息中章节列表，并按章节编号排序
        chapters = [int(i) for i in self.info['progress']
                   ['Chapter_size'] if isinstance(i, str)]
        chapters.sort()
        # 初始化将要保存的小说文件
        with open(f'./txt/{self.info["title"]}.txt', 'w', encoding='utf-8') as f:
            ...
        # 遍历章节列表，读取每个章节的内容
        for i in chapters:
            # 以只读模式打开当前章节文件
            with open(f'./txt/Cache/{self.info["title"]}/{i}', 'r', encoding='utf-8') as f:
                # 以写入模式打开目标文件
                with open(f'./txt/{self.info["title"]}.txt', 'a', encoding='utf-8') as f1:
                    # 将当前章节内容写入目标文件
                    f1.write(f.read())
                    # 在每个章节之间添加空行，以区分不同章节
                    f1.write('\n\n\n')
        # 遍历info字典，将非进度信息合并到进度信息的info字段中
        self.info['progress']['info'] = {}
        for i in self.info:
            if i == 'progress':
                continue
            self.info['progress']['info'][i] = self.info[i]
        print('小说下载成功！')

    def parse_url(self, url: Union[str, int]) -> int:
        """
        从给定的URL中尝试提取章节编号。

        参数:
        url: 需要处理的URL字符串或整数。

        返回:
        int: 提取出的章节编号，如果无法提取则返回None。
        """
        if isinstance(url, int):
            return url
        url = str(url)
        for part in url.split("/"):
            for segment in part.split("_"):
                try:
                    return int(segment)
                except ValueError:
                    continue
        return None

    def get_chapter_info(self, book_id: int, error: int = 0):
        """
        获取小说的章节目录及小说的信息

        参数:
        book_id: 小说ID
        error: 错误重试次数
        
        返回:
        Tuple[Dict[int, List[str]], Dict[str, str]]: 包含两个元素的元组。
            - 第一个元素是一个字典，键为链接在页面上的顺序，值是一个包含两个字符串的列表，
              分别代表章节的URL和标题。
            - 第二个元素是一个字典，包含页面的元数据。
        """
        url = f'http://m.ethxs.com/chapters_{book_id}/1'
        
        try:
            if self.use_proxy:
                response = requests.get(url, proxies=self.proxies, timeout=10)
            else:
                response = requests.get(url, timeout=10)
        except TimeoutError as e:
            print(f'TimeoutError: {e}')
            if error < 5:
                time.sleep(1)
                return self.get_chapter_info(book_id, error+1)
            else:
                raise
        except Exception as e:
            if error < 5:
                time.sleep(1)
                return self.get_chapter_info(book_id, error+1)
            else:
                raise
        
        html = response.text
        property_dict: Dict[str, str] = {}
        href_dict: Dict[int, List[str]] = {}
        
        # 分割HTML内容，以便处理meta标签
        meta_parts = html.split("<meta")
        # 遍历分割后的内容，提取元数据
        for part in meta_parts:
            if "property" in part:
                property_key = part.split('"')[1][3:]
                property_value = part.split("content")[1].split('"')[1]
                property_dict[property_key] = property_value
        
        # 分割HTML内容，以便处理章节链接
        chapter_list_parts = meta_parts[-1].split("章节列表")
        page_num_parts = chapter_list_parts[1].split("page_num")
        # 提取页面编号，用于构造章节链接
        page_numbers = [i.split('"')[1] for i in page_num_parts[1].split('value=')]
        
        # 遍历每个页面，提取章节链接和标题
        for i in range(len(page_numbers)-1):
            if i == 0:
                i = len(page_numbers)
            page_url = f"http://m.ethxs.com/chapters_{book_id}/{i}"
            print(page_url)
            page_html = requests.get(page_url).text
            # 分割HTML内容，提取章节链接和标题
            for j in page_html.split("章节列表")[1].split("page_num")[1].split("href")[4:]:
                temp = j.split('"')
                href_dict[len(href_dict)] = [
                    temp[1], temp[2].split('>')[1].split('<')[0]]
        
        return href_dict, property_dict

    def main(self, url: Union[str, int], name: str = '', max_workers: int = 5):
        """
        主函数，用于爬取小说的章节和内容。

        参数:
        url: 小说的URL或ID
        name: 自定义小说名称，如果为空则使用网页标题
        max_workers: 最大工作线程数
        """
        book_id = self.parse_url(url)
        href_dict, property_dict = self.get_chapter_info(book_id)
        
        if name == '':
            self.info['name'] = property_dict['title']
        else:
            self.info['name'] = name
            
        for key in property_dict:
            self.info[key] = property_dict[key]
            
        self.load_progress()
        # 确保目标目录存在
        os.makedirs(f'./txt/Cache/{self.info["title"]}/', exist_ok=True)
        # 初始化一个名为'main'的线程池执行器，用于执行主要任务
        self.executor_crawl['main'] = ThreadPoolExecutor(max_workers)
        # 将多个任务提交给线程池
        self.executor_results['main'] = [
            self.executor_crawl['main'].submit(self.crawler, i+1, href_dict[i])
            for i in range(len(href_dict))
        ]

        # 等待所有任务完成
        for i in range(len(href_dict)):
            try:
                self.executor_results['main'][i].result()
            except Exception as e:
                self.error[i] = self.executor_results['main'][i]
                
        self.write_all()
        # 保存更新后的进度信息
        self.save_progress()
        print('进度文件已保存')
