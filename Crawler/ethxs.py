"""获取ethxs.com(以太小说网的小说)
Version : 1.0.1.00
Date : 2024/07/19 17:30
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


class Old():
    """
    旧的代码，用于处理特定的网址解析和内容获取任务。
    """

    def __init__(self) -> None:
        """
        初始化解析器对象。

        此构造函数初始化解析器的状态，包括错误列表、所有解码信息的存储以及特定字段到中文描述的映射。
        """
        # 用于存储解析过程中遇到的错误
        self.error = []
        # 用于存储解码后的所有信息，以字典形式组织
        self.All: Dict[str, Any] = {
            'onDecode': {}
        }
        # 字典，用于将特定的键映射为中文描述，方便后续处理和理解
        self.Translate = {
            'type': '类型',
            'title': '小说名',
            'description': '简介',
            'image': '封面',
            'novel:category': '小说分类',
            'novel:author': '小说作者',
            'novel:book_name': '小说书名',
            'novel:read_url': '目前阅读url',
            'url': '下载url',
            'novel:status': '连载状态',
            'novel:update_time': '上次更新时间',
            'novel:latest_chapter_name': '最新章节',
            'og:novel:latest_chapter_url': '最新章节url'
        }

    def printList(self, List0):
        """
        打印列表中的所有元素及其索引。

        参数:
        List0: 待打印的列表。

        输出:
        列表中每个元素的索引和值。
        """
        print("print List start")  # 操作开始标志
        if len(List0) != 0:  # 判断列表是否为空
            for i in range(len(List0)):  # 遍历列表元素的索引
                print(i, List0[i])  # 打印元素索引和值
            print("print List End")  # 操作结束标志

    def printDict(self, Dict1):
        """
        打印字典中的所有键值对。

        参数:
        Dict1 -- 一个字典，包含要打印的键值对。
        """
        # 检查字典是否为空，如果不为空，则进行打印
        if Dict1 != {}:
            # 遍历字典中的每个键值对并打印
            for i in Dict1:
                print(i, Dict1[i])

    def printError(self, Error):
        """
        添加错误信息到错误列表中。

        此方法用于收集和记录错误信息，方便后续处理或调试。
        它通过将给定的错误信息添加到类的错误列表中来实现。

        参数:
        Error: 需要记录的错误信息。可以是任何能够表示错误的对象，例如字符串、异常实例等。
        """
        self.error.append(Error)

    def 处理网址(self, url: Union[str, int]):
        """
        从给定的URL中尝试提取章节编号。

        参数:
        url (str): 需要处理的URL字符串。

        返回:
        int: 提取出的章节编号，如果无法提取则返回None。
        """
        # 通过分割URL中的各个部分来尝试找到章节编号
        if type(url) == int:
            return url
        url = str(url)
        for i in url.split("/"):
            # 在每个部分中进一步分割以查找数字部分
            for j in i.split("_"):
                # 尝试将当前部分转换为整数，如果是数字则返回该整数
                try:
                    return int(j)
                except:
                    # 如果转换失败，则继续尝试下一个部分
                    ...

    def 获取网页(self, num):
        """
        获取特定章节编号的网页内容，并从中提取章节链接和元数据。

        参数:
        num (int): 章节编号，用于构造URL。

        返回:
        Tuple[Dict[int, List[str]], Dict[str, str]]: 包含两个元素的元组。
            - 第一个元素是一个字典，键为链接在页面上的顺序，值是一个包含两个字符串的列表，
              分别代表章节的URL和标题。
            - 第二个元素是一个字典，包含页面的元数据。
        """
        # 构造请求的URL
        url = 'chapters_' + str(num) + '/1'
        sign = []
        import requests

        # 发起HTTP请求，获取网页内容
        HTML = requests.get("http://m.ethxs.com/" + url).text
        Property: Dict[str, str] = {}
        href: Dict[int, List[str]] = {}
        # 分割HTML内容，以便处理meta标签
        List1 = HTML.split("<meta")
        # 遍历分割后的内容，提取元数据
        for i in List1:
            if "property" in i:
                Property[i.split('"')[1][3::]] = i.split(
                    "content")[1].split('"')[1]
        # 分割HTML内容，以便处理章节链接
        List2 = List1[-1].split("章节列表")
        List3 = List2[1].split("page_num")
        # 提取页面编号，用于构造章节链接
        NUM = [i.split('"')[1] for i in List3[1].split('value=')]
        # 遍历每个页面，提取章节链接和标题
        for i in range(len(NUM)-1):
            if i == 0:
                i = len(NUM)
            URL = "http://m.ethxs.com/chapters_" + str(num) + '/' + str(i)
            print(URL)
            HTMLi = requests.get(URL).text
            # 分割HTML内容，提取章节链接和标题
            for j in HTMLi.split("章节列表")[1].split("page_num")[1].split("href")[4::]:
                Temp = j.split('"')
                href[len(href)] = [
                    Temp[1], Temp[2].split('>')[1].split('<')[0]]
        return href, Property

    def 获取正文(self, href) -> Dict[str, str]:
        """
        从指定的网页链接中获取小说的章节名称和正文文本。

        参数:
        href: 包含章节链接和章节名称的元组。

        返回:
        一个字典，包含章节名称和章节文本。
        """
        # 初始化页面编号和存储小说文本的字符串
        page = 0
        Text = ''
        while True:
            # 根据页面编号构建章节的URL
            if page == 0:
                pageUrl = "http://m.ethxs.com/" + href[0]
            else:
                pageUrl = "http://m.ethxs.com/" + \
                    href[0].split(".html")[0] + '_' + str(page) + ".html"
            # 发送HTTP请求获取页面内容
            respond = requests.get(pageUrl, allow_redirects=False)
            # 如果收到301重定向响应，结束循环
            if respond.status_code == 301:
                break
            # 从响应中提取HTML内容
            HTML = respond.text
            # 解析HTML，提取小说正文文本
            List1 = HTML.split('id="txt"')[1].split(
                '</br>')[0].split("/script")[:-1:]
            # 更新页面编号
            page += 1
            # 遍历提取的文本片段，存储并翻译小说正文
            for x in range(len(List1)):
                self.All['onDecode'][x] = List1[x].split("'")[1]
                Text += self.翻译小说正文(List1[x].split("'")[1]) + '\n'
            # 清空存储文本片段的字典，准备下一次填充
            self.All['onDecode'] = {}
            # 输出进度符号
            print(end='█')
        # 构建并返回包含章节名称和正文文本的字典
        output = {"chapter_name": href[1], "text": Text}
        return output

    def 翻译小说正文(self, input: str) -> str:
        """
        解密小说正文的函数。

        使用Base64解码方法对输入的字符串进行解码，以恢复原始文本。

        参数:
        input: 待解密的字符串

        返回:
        解密后的字符串
        """
        # 定义Base64编码表
        keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
        # 构建Base64编码与数字的映射字典
        _keyStr = {keyStr[i]: i for i in range(len(keyStr))}

        # 初始化原始文本
        Text = input
        # 初始化解码后的文本
        utftext = ""

        # 移除编码中不合法的字符
        for x in input:
            if x not in _keyStr:
                Text = Text.replace(x, '')
                print("删除\n\n\n\n\n", x)

        # 将原始文本转换为编码数字列表
        enc = [_keyStr[item] for item in Text]

        # 检查编码长度是否符合要求，否则报错
        if len(enc) % 4 != 0:
            self.printError('Error:解密错误(密码位数不正确)\n    解密内容：{}'.format(input))
        else:
            # 根据编码数字列表解码
            for i in range(int(len(enc)/4)):
                Chr = [(enc[4*i] << 2 | enc[4*i+1] >> 4), ((enc[4*i+1] & 15) << 4)
                       | (enc[4*i+2] >> 2), ((enc[4*i+2] & 3) << 6) | enc[4*i+3]]
                # 将解码后的字符添加到解码文本中
                utftext += chr(Chr[0])
                if enc[2] != 64:
                    utftext += chr(Chr[1])
                if enc[3] != 64:
                    utftext += chr(Chr[2])

        # 将换行符统一为'\n'
        utftext = utftext.replace("\r", "\n")
        # 初始化输出字符串
        output = ""
        # 初始化解码状态变量
        n = 0
        c = [0, 0, 0]

        # 解码UTF-8文本
        while n < len(utftext):  # 对应函数 qsbs._utf8_decode()
            c[0] = ord(utftext[n])
            if c[0] < 128:
                output += chr(c[0])
                n += 1
            elif c[0] > 191 and c[0] < 224:
                c[1] = ord(utftext[n+1])
                output += chr(((c[0] & 31) << 6) | (c[1] & 63))
                n += 2
            else:
                c[1] = ord(utftext[n + 1])
                c[2] = ord(utftext[n + 2])
                output += chr(((c[0] & 15) << 12) |
                              ((c[1] & 63) << 6) | (c[2] & 63))
                n += 3

        # 返回最终解密后的文本
        return output[3:-6:]

    def main(self, url: (str or int), name: str = ''):
        """
        主函数，负责整体流程的执行。

        参数:
        url: 需要处理的网址或编号。
        name: 保存文件的名称，默认为空，会使用网页标题作为名称。
        """
        # 导入时间模块，用于计算执行时间
        import time

        # 记录开始时间
        time_0 = time.time()

        # 处理网址或编号，获取具体的处理数字
        num = self.处理网址(url)
        # 根据处理数字，获取网页链接和属性信息
        href, Property = self.获取网页(num)

        # 初始化存储所有文本内容的字典
        self.All['text'] = []
        # 遍历所有链接，下载正文内容
        for i in range(len(href)):
            # 打印下载进度
            print('\n正在下载:第', i+1, '章', end='')
            # 获取并存储正文内容
            self.All['text'].append(self.获取正文(href[i]))

        # 记录结束时间
        time_1 = time.time()
        # 打印总耗时
        print('下载完成，共耗时', time_1-time_0, '秒')
        # 计算并打印平均速度
        print('平均速度：', '{}s/章'.format((time_1-time_0)/len(href)))

        # 打印错误列表
        self.printList(self.error)

        # 如果没有提供文件名，则使用网页标题作为文件名
        if name == '':
            name = Property['title']
        # 打开文件，准备写入内容
        with open(name+'.txt', 'w', encoding='utf-8') as f:
            # 遍历属性字典，写入文件（跳过包含'url'的键）
            for i in Property:
                if 'url' in i:
                    continue
                try:
                    # 尝试使用预定义的翻译函数转换键名，然后写入值
                    f.write('{}.{}'.format(self.Translate[i], Property[i]))
                except:
                    # 如果转换失败，直接写入键名和值
                    f.write('{}.{}'.format(i, Property[i]))
                f.write('\n')
            # 写入空行，然后写入源数据字典的字符串表示
            f.write('\n'*2)
            f.write('源数据:\n')
            f.write(str(Property))
            f.write('\n'*2)
            f.write('\n')
            # 遍历所有文本内容，写入文件
            for x in self.All['text']:
                f.write(x['chapter_name'])
                f.write('\n')
                f.write(x['text'])


class Main():
    """
    经过重构后的代码
    """

    def __init__(self) -> None:
        """
        初始化示例类的属性。

        初始化包括定义用于编码和解码的字典结构，设置线程池执行器以及初始化一个用于旧系统兼容性的实例。
        """
        # 定义一个字典，用于存储待解码文本，键为整数，值为另一个字典，该字典的键为整数，值为字符串列表。
        self.code: Dict[int, Dict[int, List[str]]] = {}
        # 定义一个字典，用于存储解码后的结果，键可以是任意类型，值为字符串。
        self.Decoded: Dict[Any, str] = {}
        # 定义一个通用信息字典，用于存储各种相关信息。
        self.info: Dict[str, Any] = {}
        # 定义一个字典，用于存储线程池执行器实例
        self.exeCrawl: Dict[str, thread.ThreadPoolExecutor] = {}
        # 定义一个字典，用于存储线程池执行器的任务结果
        self.exeResults: Dict[str, List[_base.Future]] = {}
        # 初始化一个老代码的实例，用于处理旧代码的兼容性问题。
        self.Old = Old()
        # 定义一个列表，用于存储被删除的章节信息
        self.deleted: Dict[int,List[str]] = {}
        # 定义一个布尔值，用于指示是否使用代理（请自行使用）
        self.ifproxies = False
        # 定义一个字典，用于存储代理信息（请自行使用）
        self.proxies = {
            'http': '',
            'https': ''
        }
        self.Error:Dict[int,_base.Future] ={}

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

    def Crawler(self, N: int, href: List[str]):
        """
        爬虫函数，用于下载指定小说的指定章节。

        参数:
        N: int - 需要下载的章节编号
        href: List[str] - 小说的URL列表，其中href[0]是小说主页的URL，href[1]是小说目录的URL
        """
        # 检查章节是否已经下载过，如果已经下载并且与缓存文件大小相同，则不再下载
        if str(N) in (self.info['progress']['Chapter_size']):
            if os.path.getsize(f'./txt/Cache/{self.info["title"]}/{N}') == self.info['progress']['Chapter_size'][str(N)]:
                return
        # 输出开始下载的提示信息
        print(f'开始下载第{N}章')
        page = 0
        self.code[N] = {}
        # 开始循环下载页面，直到无法获取页面为止
        while page >= 0:
            # 对于第一页，使用小说主页的URL；对于后续页面，构造相应的URL
            if page == 0:
                # 构造小说第一章的URL
                pageUrl = "http://m.ethxs.com/" + href[0]
            else:
                # 构造后续章节的URL
                pageUrl = "http://m.ethxs.com/" + \
                    href[0].split(".html")[0] + '_' + str(page) + ".html"
            # 尝试获取页面，如果成功，则继续获取下一页；如果失败，则结束循环
            if self.GetPageN(pageUrl, N, page):
                # 如果成功获取到页面，尝试获取下一页
                page += 1
            else:
                # 如果无法获取到页面，结束爬取
                page = -1
        if self.code[N] == {}:
            print('第{N}章下载失败')
            return
        # 解码下载的章节内容
        self.Decode(Chapter=N)
        # 将解码后的章节写入文件
        self.Write(N, href[1])

    def GetPageN(self, url, Chapter: int, Page: int, error: int = 0) -> bool:
        """
        从给定的URL获取小说的指定章节和页面。

        参数:
        url (str): 小说章节页面的URL。
        Chapter (int): 章节的编号。
        Page (int): 页面的编号。
        error (int): 当前的错误计数，用于重试机制，默认为0。

        返回:
        bool: 如果成功获取页面，则返回True；否则返回False。
        """
        # 尝试发送HTTP请求获取页面
        try:
            if self.ifproxies:
                respond = requests.get(
                    url, allow_redirects=False, proxies=self.proxies)
            else:
                respond = requests.get(url, allow_redirects=False)
        except:
            # 如果请求失败，根据错误计数决定是否重试
            if error < 5:
                time.sleep(5)  # 等待5秒后重试
                return self.GetPageN(url, Chapter, Page, error+1)
            else:
                print(f"第{Chapter}章第{Page}下载失败")
                self.code[Chapter][Page] = ['']
                return False
        else:
            # 如果请求重定向，视为完成本章下载
            if respond.status_code == 301:
                return False
            # 从响应中提取HTML内容
            HTML = respond.text
            # 提取正文中的密文
            code = self.extract_texts_from_html(HTML)
            # 删除HTML，减少资源占用
            del HTML
            # 将处理得到的密文写入self.code中
            self.code[Chapter][Page] = code
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

    def Old_Decode(self, Chapter: int = -1, code: str = '') -> None:
        """
        解码指定章节或代码。

        如果Chapter参数为-1且code参数不为空，则认为是解码字符串。
        如果Chapter参数不为-1且code参数为空，则认为是解码指定章节。

        :param Chapter: int，指定要解码的章节编号，默认为-1，表示解码字符串。
        :param code: str，待解码的字符串，默认为空。
        :return: None，但会更新self.Decoded属性。
        """
        # 当章节参数为默认值-1且code不为空时，解码字符串
        if Chapter == -1 and code != '':
            # 使用Old对象的翻译方法解码小说正文，并将结果存储在Decoded字典中
            self.Decoded['Decode'] = self.Old.翻译小说正文(code)
        # 当章节参数不为默认值且code为默认值空时，解码指定章节
        elif Chapter != -1 and code == '':
            # 获取指定章节的解码信息
            decode = self.code[Chapter]
            decoded_parts: List[str] = []
            # 遍历解码信息中的每个部分，进行解码
            for i in decode:
                for j in decode[i]:
                    # 使用老代码的翻译方法解码每个部分
                    decoded_parts.append(self.Old.翻译小说正文(j))
            # 将解码后的部分合并成字符串，以换行符分隔，并存储在Decoded字典的对应章节中
            self.Decoded[Chapter] = '\n'.join(decoded_parts)

    def Decode(self, Chapter: int = -1, code: str = '') -> None:
        """
        解码指定章节或代码。

        如果Chapter参数为-1且code参数不为空，则认为是解码字符串。
        如果Chapter参数不为-1且code参数为空，则认为是解码指定章节。

        参数:
        Chapter: int，指定要解码的章节编号，默认为-1，表示解码字符串。
        code: str，待解码的字符串，默认为空

        返回:
        None，但会更新self.Decoded
        """
        # 当章节参数为默认值-1且code不为空时，解码字符串
        if Chapter == -1 and code != '':
            # 使用base64解码小说正文，并将结果存储在Decoded字典中
            self.Decoded['Decode'] = base64.b64decode(code).decode('utf-8')
        # 当章节参数不为默认值且code为默认值空时，解码指定章节
        elif Chapter != -1 and code == '':
            # 获取指定章节的解码信息
            decode = self.code[Chapter]
            decoded_parts: List[str] = []
            # 初始化一个布尔值，用于判断是否需要删除
            delete = False
            # 遍历解码信息中的每个部分，进行解码
            for i in decode:
                for j in decode[i]:
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
                        if not Chapter in self.deleted:
                            self.deleted[Chapter] = []
                        self.deleted[Chapter].append(decoded)
                    else:
                        # 将解码后的部分添加到列表中
                        decoded_parts.append(decoded)
            # 将解码后的部分合并成字符串，以换行符分隔，并存储在Decoded字典的对应章节中
            self.Decoded[Chapter] = '\n'.join(
                decoded_parts).replace('<p>—</p>', '\n')
            # 删除已解码的code
            del self.code[Chapter]

    def Write(self, Chapter: int, Chapter_Name):
        """
        将章节名称和内容写入到指定章节的文本文件中。

        参数:
        Chapter: int, 章节的编号，用于生成文件名和作为字典的键。
        Chapter_Name: str, 章节的名称，将写入文件作为章节标题。
        """
        # 判断文件是否存在
        if os.path.exists(f'./txt/Cache/{self.info["title"]}/{Chapter}'):
            # 如果存在就删除文件
            os.remove(f'./txt/Cache/{self.info["title"]}/{Chapter}')
        # 使用with语句确保文件正确打开和关闭，以utf-8编码写入
        with open(f'./txt/Cache/{self.info["title"]}/{Chapter}', 'w', encoding='utf-8') as f:
            # 写入章节标题
            f.write(f'{Chapter_Name}\n')
            # 写入章节内容
            f.write(self.Decoded[Chapter])
        # 更新当前章节的进度信息(章节大小)
        self.info['progress']['Chapter_size'][str(Chapter)] = os.path.getsize(
            f'./txt/Cache/{self.info["title"]}/{Chapter}')
        # 从Decoded字典中删除已处理的章节，减少资源占用
        del self.Decoded[Chapter]

    def WriteAll(self):
        """
        将所有章节内容合并写入到一个单独的文本文件中。

        本函数首先从缓存目录中读取每个章节的文本内容，然后将这些内容写入到一个名为
        标题.txt的文件中，每个章节之间用空行分隔。此外，它还会更新进度信息，将
        其余信息合并到进度信息中，并保存更新后的进度。
        """
        # 获取进度信息中章节列表，并按章节编号排序
        Chapter = [int(i) for i in self.info['progress']
                   ['Chapter_size'] if isinstance(i, str)]
        Chapter.sort()
        # 初始化将要保存的小说文件
        with open(f'./txt/{self.info["title"]}.txt', 'w', encoding='utf-8') as f:
            ...
        # 遍历章节列表，读取每个章节的内容
        for i in Chapter:
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

    def Get_Chapter(self, num, error: int = 0):
        """
        获取小说的章节目录及小说的信息
        """
        url = 'chapters_' + str(num) + '/1'
        if self.ifproxies:
            try:
                HTML = requests.get(url, proxies=self.proxies, timeout=10)
            except TimeoutError as e:
                print(f'TimeoutError{e}')
            except:
                if error > 5:
                    raise
                else:
                    time.sleep(1)
                    return self.Get_Chapter(num, error+1)
        else:
            try:
                HTML = requests.get(url, timeout=10)
            except TimeoutError as e:
                print(f'TimeoutError{e}')
            except:
                if error > 5:
                    raise
                else:
                    time.sleep(1)
                    return self.Get_Chapter(num, error+1)

    def main(self, url: Union[str, int], name: str = '',max_workers:int = 5):
        """
        主函数，用于爬取小说的章节和内容。
        """
        num = Old().处理网址(url)
        href, Property = self.Old.获取网页(num)
        if name == '':
            self.info['name'] = Property['title']
        else:
            self.info['name'] = name
        for i in Property:
            self.info[i] = Property[i]
        self.load_progress()
        # 确保目标目录存在
        os.makedirs(f'./txt/Cache/{self.info["title"]}/', exist_ok=True)
        # 初始化一个名为'main'的线程池执行器，用于执行主要任务，最大工作线程数为5。
        self.exeCrawl['main'] = ThreadPoolExecutor(max_workers)
        # 将多个任务提交给线程池
        self.exeResults['main'] = [self.exeCrawl['main'].submit(
            self.Crawler, i+1, href[i])for i in range(len(href))]

        # 等待所有任务完成
        for i in range(len(href)):
            try:
                self.exeResults['main'][i].result()
            except:
                self.Error[i] = self.exeResults['main'][i]
        self.WriteAll()
        # 保存更新后的进度信息
        self.save_progress()
        print('进度文件已保存')
