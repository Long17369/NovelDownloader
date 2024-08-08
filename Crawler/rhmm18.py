"""获取rhmm18.com(零点看书)
Version : 1.0.0.00(未完工)
Date : 2024/08/06 13:20
Author : Long17369
"""

import json
import os
import time
from typing import List, Dict, Any, Union
from concurrent.futures import ThreadPoolExecutor, _base, thread
import requests
import bs4


class Main:
    def __init__(self,):
        self.href: Dict[int, List[str]] = {}
        self.failed : List[int] = []
        self.no: Dict[int, str] = {}
        self.text: Dict[int, Dict[int, str]] = {}
        self.exeCrawl: Dict[str, thread.ThreadPoolExecutor] = {}
        self.exeResults: Dict[str, List[_base.Future]] = {}
        self.info : Dict[str, Any] = {}
        self.ifproxies = False
        self.proxies = {
            'http': '',
            'https': ''
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.37'
        }

    def get(self, url, error: int = 0) -> requests.Response:
        if self.ifproxies:
            try:
                res = requests.get(url, proxies=self.proxies,
                                   timeout=10, headers=self.headers)
                return res
            except:
                if error < 5:
                    time.sleep(3)
                    return self.get(url, error + 1)
                else:
                    raise
        else:
            try:
                res = requests.get(url, timeout=10, headers=self.headers)
                return res
            except:
                if error < 5:
                    time.sleep(3)
                    return self.get(url, error + 1)
                else:
                    raise

    def GetPageN(self, url, Chapter: int, Page: int) -> bool:
        res = self.get(url)
        if res.status_code == 404:
            return False
        res.encoding = 'utf-8'
        soup = bs4.BeautifulSoup(res.text,'html.parser')
        tags = soup.find_all('div',id="chaptercontent")[0]
        tag = [i.text.replace('\r','') for i in tags.find_all('p')]
        self.text[Chapter][Page] = '\n'.join(tag)
        return True

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

    def Get_property(self, num) -> Dict[str, str]:
        res = self.get(f'https://www.rhmm18.com/{num//1000}_{num}/')
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        Property = {i['property'][3:]: i['content'] for i in [
            i.attrs for i in soup.find_all('meta')] if 'property' in i}
        return Property

    def Get_Chapter(self, num):
        href: Dict[int, List[str]] = {}
        Page = 1
        url = f'https://www.rhmm18.com/indexlist/{num}/'+'{Page}/'
        while True:
            print(url.format(Page=Page))
            res = self.get(url.format(Page=Page))
            if res.status_code == 404:
                break
            else:
                Page += 1
                HTML = res.text
                soup = bs4.BeautifulSoup(HTML, 'html.parser')
                Href = [i.find('a').attrs for i in soup.find_all(
                    'div', class_='chapterlist')[0].find_all('ul')[0].find_all('li')]
                for i in range(len(Href)):
                    if 'class' in Href[i]:
                        Href[i]['href'] = ''
                    else:
                        Href[i]['href'] = Href[i]['onclick'].split("/")[-1][:-6]
                for i in range(len(Href)):
                    href[len(href)+1] = [Href[i]['href'],Href[i]['title']]
        self.no = {i:href[i][1] for i in href if href[i][0]==''}
        return href

    def urlhandler(self, url: Union[str, int]):
        if isinstance(url, int):
            return url
        else:
            url = url.split('_')[-1]
            return int(url)

    def Crawler(self, N: int, href: List[str]):
        if str(N) in (self.info['progress']['Chapter_size']):
            if os.path.getsize(f'./txt/Cache/{self.info["title"]}/{N}') == self.info['progress']['Chapter_size'][str(N)]:
                return True
        print(f'正在下载{href[1]}')
        page = 1
        self.text[N] = {}
        while page >= 1:
            if page == 1:
                pageurl = f'https://www.rhmm18.com/{self.num//1000}_{self.num}/{href[0]}.html'
            else:
                pageurl = f'https://www.rhmm18.com/{self.num//1000}_{self.num}/{href[0]}_{page}.html'
            # print(f'下载第{page}页')
            if self.GetPageN(pageurl,N,page):
                page += 1
            elif page == 1:
                self.failed.append(N)
                print(f'第{N}章下载失败')
                return False
            else:
                page = -1
        self.Write(N,href[1])
        if N in self.failed:
            self.failed.remove(N)
        return True

    def Write(self, Chapter: int, Chapter_Name) -> None:
        if os.path.exists(f'./txt/Cache/{self.info["title"]}/{Chapter}'):
            os.remove(f'./txt/Cache/{self.info["title"]}/{Chapter}')
        with open(f'./txt/Cache/{self.info["title"]}/{Chapter}', 'w', encoding='utf-8') as f:
            f.write(f'{Chapter_Name}\n')
            f.write('\n '.join([self.text[Chapter][i] for i in self.text[Chapter]]))
        self.info['progress']['Chapter_size'][str(Chapter)] = os.path.getsize(f'./txt/Cache/{self.info["title"]}/{Chapter}')
        del self.text[Chapter]

    def WriteAll(self):
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

    def No(self, N:int):
        for i in range(int(self.href[N-1][0]), int(self.href[N+1][0])):
            try:
                if self.Crawler(N,[str(i),self.no[N]]):
                    return
            except:
                pass

    def main(self, url: Union[str, int], name: str = '', max_workers: int = 5):
        num = self.urlhandler(url)
        self.num = num
        self.href = self.Get_Chapter(num)
        Property = self.Get_property(num)
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
            self.Crawler, i,self.href[i])for i in self.href if self.href[i][0] != '']
        self.exeResults['main'] += [self.exeCrawl['main'].submit(self.No,i)for i in self.no]
        for i in self.exeResults['main']:
            try:
                i.result()
            except:
                pass
        self.WriteAll()
        self.save_progress()
