"""获取ethxs.com(以太小说网的小说)
Version : 1.0.0.0
Date : 2024/06/24 20:00
Author : Long17369
"""


from typing import Dict
import requests


def printList(List0):
    print("print List start")
    for i in range(len(List0)):
        print(i, List0[i])
    print("print List End")


def 获取网页(num):
    url = 'chapters_'+str(num)+'/1'
    sign = []
    HTML = requests.get("https://m.ethxs.com/"+url).text
    Property = []
    href: Dict[int, str] = {}
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
    for i in range(len(NUM)):
        if i == 0:
            i = len(NUM)
        HTMLi = requests.get(
            "https://m.ethxs.com/chapters_"+str(num)+'/'+str(i)).text
        HTMLi.split("章节列表")
        for j in List3[1].split("href"):
            href[len(href)] = j
            print(j)
    # printList(href)


if __name__ == "__main__":
    url = input("网页https://m.ethxs.com/")
    for i in url.split("/"):
        stop = False
        # print(i)
        for j in i.split("_"):
            # print(j)
            try:
                # print(int(j))
                url = int(j)
                stop = True
                break
            except:
                ...
                # print('Error')
        if stop:
            break
    获取网页(url)
    # print('结果:', url)
