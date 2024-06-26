"""获取ethxs.com(以太小说网的小说)
Version : 1.0.0.0
Date : 2024/06/24 20:00
Author : Long17369
"""


from typing import Dict, List
import requests


error = []


def printList(List0):
    print("print List start")
    for i in range(len(List0)):
        print(i, List0[i])
    print("print List End")


def printError(Error):
    error.append(Error)


def 处理网址(url):
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


def 获取网页(num):
    url = 'chapters_' + str(num) + '/1'
    sign = []
    HTML = requests.get("https://m.ethxs.com/" + url).text
    Property = []
    # href 格式: dict[int, list['url','chapter_name']]
    href: Dict[int, list] = {}
    List1 = HTML.split("<meta")
    for i in List1:
        if "property" in i:
            Property.append(i.split("content")[1].split('"')[1])
            # print(Property)
    List2 = List1[-1].split("章节列表")
    # printList(List2)
    List3 = List2[1].split("page_num")
    # printList(List3)
    NUM = [i.split('"')[1] for i in List3[1].split('value=')]
    printList(NUM)
    for i in range(len(NUM)-1):
        if i == 0:
            i = len(NUM)
        URL = "https://m.ethxs.com/chapters_" + str(num) + '/' + str(i)
        print(URL)
        HTMLi = requests.get(URL).text
        for j in HTMLi.split("章节列表")[1].split("page_num")[1].split("href")[4::]:
            Temp = j.split('"')
            href[len(href)] = [Temp[1], Temp[2].split('>')[1].split('<')[0]]
    printList(href)
    return href


def 获取正文(href) -> Dict[str, str]:
    """用于获取小说的正文\n
    href指一章小说的第一页
    """
    page = 0
    print(href[1])
    Text = ''
    while True:
        if page == 0:
            pageUrl = "https://m.ethxs.com/" + href[0]
        else:
            pageUrl = "https://m.ethxs.com/" + \
                href[0].split(".html")[0] + '_' + str(page) + ".html"
        print(pageUrl)
        respond = requests.get(pageUrl, allow_redirects=False)
        print(respond.status_code)
        if respond.status_code == 301:
            break
        HTML = respond.text
        List1 = HTML.split('id="txt"')[1].split(
            '</br>')[0].split("/script")[:-1:]
        for x in range(len(List1)):
            print("    ", x,List1[x].split("'")[1])
        page += 1
        print(len(List1))
        for x in range(len(List1)):
            print(x)
            Text += 翻译小说正文(List1[x].split("'")[1]) + '\n'
    return {"chapter_name": href[1], "text": Text}


def 翻译小说正文(input: str) -> str:
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
        printError('Error:解密错误(密码位数不正确)\n    解密内容：{}'.format(input))
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
        else:
            printList(c)
            printList([ord(utftext[x]) for x in range(len(utftext))])
            print(n)
            c[1] = ord(utftext[n + 1])
            print(utftext[n + 2])
            c[2] = ord(utftext[n + 2])
            output += chr(((c[0] & 15) << 12) |
                          ((c[1] & 63) << 6) | (c[2] & 63))
            n += 3
    print(output)
    return output


if __name__ == "__main__":
    url = input("网页https://m.ethxs.com/")
    num = 处理网址(url)
    href = 获取网页(num)
    text: List[Dict[str, str]] = [{}]
    for i in range(len(href)):
        text.append(获取正文(href[i]))
    print(text)
    printList(error)
    # print('结果:', url)
