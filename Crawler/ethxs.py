"""获取ethxs.com(以太小说网的小说)
Version : 1.0.0.2
Date : 2024/07/14 15:00
Author : Long17369
"""


from typing import Dict, List, Any
import requests


class Old():
    """
    旧的代码
    """
    def __init__(self) -> None:
        self.error = []
        self.All: Dict[str, Any] = {
            'onDecode': {}
        }
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
    
    def printList(self,List0):
        print("print List start")
        if len(List0) != 0:
            for i in range(len(List0)):
                print(i, List0[i])
            print("print List End")


    def printDict(self,Dict1):
        if Dict1 != {}:
            for i in Dict1:
                print(i, Dict1[i])


    def printError(self,Error):
        self.error.append(Error)


    def 处理网址(self,url):
        for i in url.split("/"):
            # print(i)
            for j in i.split("_"):
                # print(j)
                try:
                    # print(int(j))
                    url = int(j)
                    return int(j)
                    break
                except:
                    ...


    def 获取网页(self,num):
        url = 'chapters_' + str(num) + '/1'
        sign = []
        import requests
        HTML = requests.get("https://m.ethxs.com/" + url).text
        Property = {}
        # href 格式: dict[int, list['url','chapter_name']]
        href: Dict[int, list] = {}
        List1 = HTML.split("<meta")
        for i in List1:
            if "property" in i:
                Property[i.split('"')[1][3::]] = i.split(
                    "content")[1].split('"')[1]
                # printDict(Property)
        List2 = List1[-1].split("章节列表")
        # printList(List2)
        List3 = List2[1].split("page_num")
        # printList(List3)
        NUM = [i.split('"')[1] for i in List3[1].split('value=')]
        # printList(NUM)
        for i in range(len(NUM)-1):
            if i == 0:
                i = len(NUM)
            URL = "https://m.ethxs.com/chapters_" + str(num) + '/' + str(i)
            print(URL)
            HTMLi = requests.get(URL).text
            for j in HTMLi.split("章节列表")[1].split("page_num")[1].split("href")[4::]:
                Temp = j.split('"')
                href[len(href)] = [Temp[1], Temp[2].split('>')[1].split('<')[0]]
        # printList(href)
        return href, Property


    def 获取正文(self,href) -> Dict[str, str]:
        """用于获取小说的正文\n
        href指一章小说的第一页
        """
        page = 0
        # print(href[1])
        Text = ''
        while True:
            if page == 0:
                pageUrl = "https://m.ethxs.com/" + href[0]
            else:
                pageUrl = "https://m.ethxs.com/" + \
                    href[0].split(".html")[0] + '_' + str(page) + ".html"
            # print(pageUrl)
            respond = requests.get(pageUrl, allow_redirects=False)
            # print(respond.status_code)
            if respond.status_code == 301:
                break
            HTML = respond.text
            List1 = HTML.split('id="txt"')[1].split(
                '</br>')[0].split("/script")[:-1:]
            # for x in range(len(List1)):
            #     print("    ", x,List1[x].split("'")[1])
            page += 1
            # print(len(List1))
            for x in range(len(List1)):
                # print(x)
                self.All['onDecode'][x] = List1[x].split("'")[1]
                Text += self.翻译小说正文(List1[x].split("'")[1]) + '\n'
            self.All['onDecode'] = {}
            print(end='█')
        output = {"chapter_name": href[1], "text": Text}
        # printDict(output)
        return output


    def 翻译小说正文(self,input: str) -> str:
        keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
        _keyStr = {keyStr[i]: i for i in range(len(keyStr))}
        Text = input
        utftext = ""
        for x in input:
            if x not in _keyStr:
                Text = Text.replace(x, '')
                print("删除\n\n\n\n\n", x)
        enc = [_keyStr[item] for item in Text]
        if len(enc) % 4 != 0:
            self.printError('Error:解密错误(密码位数不正确)\n    解密内容：{}'.format(input))
        else:
            for i in range(int(len(enc)/4)):
                Chr = [(enc[4*i] << 2 | enc[4*i+1] >> 4), ((enc[4*i+1] & 15) << 4)
                    | (enc[4*i+2] >> 2), ((enc[4*i+2] & 3) << 6) | enc[4*i+3]]
                utftext += chr(Chr[0])
                if enc[2] != 64:
                    utftext += chr(Chr[1])
                if enc[3] != 64:
                    utftext += chr(Chr[2])
        utftext = utftext.replace("\r", "\n")
        output = ""
        n = 0
        c = [0, 0, 0]
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
                # printList(c)
                # printList([ord(utftext[x]) for x in range(len(utftext))])
                # print(n)
                c[1] = ord(utftext[n + 1])
                # print(utftext[n + 2])
                c[2] = ord(utftext[n + 2])
                output += chr(((c[0] & 15) << 12) |
                            ((c[1] & 63) << 6) | (c[2] & 63))
                n += 3
            # print(end=' ')
        # print(output[3:-7:])
        # print(end='█')
        return output[3:-6:]


    def main(self,url: (str or int), name: str = ''):
        import time
        time_0 = time.time()
        num = self.处理网址(url)
        href, Property = self.获取网页(num)
        self.All['text'] = []
        for i in range(len(href)):
            print('\n正在下载:第', i+1, '章', end='')
            self.All['text'].append(self.获取正文(href[i]))
        time_1 = time.time()
        print('下载完成，共耗时',time_1-time_0,'秒')
        print('平均速度：','{}s/章'.format((time_1-time_0)/len(href)))
        # printList(All['text'])
        self.printList(self.error)
        if name == '':
            name = Property['title']
        with open(name+'.txt', 'w', encoding='utf-8') as f:
            for i in Property:
                if 'url' in i:
                    continue
                try:
                    f.write('{}.{}'.format(self.Translate[i], Property[i]))
                except:
                    f.write('{}.{}'.format(i, Property[i]))
                f.write('\n')
            f.write('\n'*2)
            f.write('源数据:\n')
            f.write(str(Property))
            f.write('\n'*2)
            f.write('\n')
            for x in self.All['text']:
                f.write(x['chapter_name'])
                f.write('\n')
                f.write(x['text'])


# 定义一个任务函数
def Crawler(n):
    print(f"Processing {n}")
    return f"Task {n} is done"


# 使用线程池执行任务
def main(url: (str or int), name: str = ''):
    from typing import List
    from concurrent.futures import ThreadPoolExecutor
    num = Old().处理网址(url)
    href, Property = Old().获取网页(num)
    with ThreadPoolExecutor(max_workers=5) as executor:  # 线程数为 5
        # 将多个任务提交给线程池
        results = [executor.submit(Crawler, i) for i in href]

        # 等待所有任务完成，并获取结果
        for future in results:
            print(future.result())
