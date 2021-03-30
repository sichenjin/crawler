import random
import threading

import requests
from bs4 import BeautifulSoup
import os
import json 
import time
import random

import traceback
from string import Template
from pyquery import PyQuery as pq
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

url_list = ['https://www.csdn.net/nav/python?spm=1000.2115.3001.4125','https://www.csdn.net/nav/java?spm=1000.2115.3001.4125','https://www.csdn.net/nav/arch?spm=1000.2115.3001.4125',
'https://ai.csdn.net/?spm=1000.2115.3001.4125','https://www.csdn.net/nav/mobile','https://www.csdn.net/nav/career?spm=1000.2115.3001.4125',
'https://www.csdn.net/nav/fund?spm=1000.2115.3001.4125','https://www.csdn.net/nav/iot?spm=1000.2115.3001.4125',
'https://www.csdn.net/nav/web?spm=1000.2115.3001.4125','https://blockchain.csdn.net/',
'https://www.csdn.net/nav/game?spm=1000.2115.3001.4125','https://www.csdn.net/nav/ops?spm=1000.2115.3001.4125',
'https://www.csdn.net/nav/5g?spm=1000.2115.3001.4125','https://www.csdn.net/nav/avi?spm=1000.2115.3001.4125',
'https://www.csdn.net/nav/engineering?spm=1000.2115.3001.4125','https://www.csdn.net/nav/sec?spm=1000.2115.3001.4125',
'https://ac.csdn.net/?spm=1000.2115.3001.4125','https://www.csdn.net/nav/db?spm=1000.2115.3001.4125',
'https://cloud.csdn.net/']
tag_name = [
    'Python','Java','架构','人工智能','移动开发','程序人生','计算机基础'
    , '物联网','前端','区块链','游戏开发','运维','5G','音视频开发',
    '研发管理','信息安全','能力认证','数据库','云计算'
]
# urlTmpl = Template(
#     'https://segmentfault.com/t/${tagId}/blogs?page=${page}')
base_url = 'https://www.csdn.net/'

# def fill_tmpl(tag,page):
#     return urlTmpl.substitute(
#         page=page, tagId=tag)


def get_page(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'}
    r = requests.get(url,headers = headers)
    r.encoding = 'utf-8'
    return r.text


# def get_tag_name(url):  #得到所有的分类
#     html=get_page(url)
#     soup=BeautifulSoup(html,'html.parser')
#     all_tag_li=soup.find_all('li',{'class':{'tagPopup'}})
#     tag_name = []
#     for li in all_tag_li:
#         big_cate = li.find('a').text.strip()
#         # big_url= fill_tmpl(big_cate)
#         tag_name.append(big_cate)
#     return tag_name


def get_recipe_url(cate_url):  #得到每个类别里面所有页的上面的文章的url
    # chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(executable_path='/root/geckodriver',options=options)
    driver.get(cate_url)
    time.sleep(3)
    # driver.set_window_size(1000,30000)
    # driver.maximize_window()
    # driver.find_element_by_xpath('//input[@class="readerImg"]').send_keys(Keys.HOME)
    # js="var q=document.documentElement.scrollTop=1000000"  
    # driver.execute_script(js)  
    # 获取页面初始高度
    js = "return action=document.body.scrollHeight"
    height = driver.execute_script(js)

    # 将滚动条调整至页面底部
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
    time.sleep(5)
    
    #定义初始时间戳（秒）
    t1 = int(time.time())

    #定义循环标识，用于终止while循环
    scroll_times = 1000

    # 重试次数
    num=0

    while scroll_times:
        new_height = driver.execute_script(js)
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        scroll_times = scroll_times -1

        # # 获取当前时间戳（秒）
        # t2 = int(time.time())
        # # 判断时间初始时间戳和当前时间戳相差是否大于30秒，小于30秒则下拉滚动条
        # if t2-t1 < 30:
        #     new_height = driver.execute_script(js)
        #     if new_height > height :
        #         time.sleep(1)
        #         driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        #         # 重置初始页面高度
        #         height = new_height
        #         # 重置初始时间戳，重新计时
        #         t1 = int(time.time())
        # elif num < 3:                        # 当超过30秒页面高度仍然没有更新时，进入重试逻辑，重试3次，每次等待30秒
        #     time.sleep(3)
        #     num = num+1
        # else:    # 超时并超过重试次数，程序结束跳出循环，并认为页面已经加载完毕！
        #     print("滚动条已经处于页面最下方！")
        #     status = False
        #     # 滚动条调整至页面顶部
        #     driver.execute_script('window.scrollTo(0, 0)')
        #     break


    soup = BeautifulSoup(driver.page_source,'lxml')

    recipe_url=[]
    # page = 1
    # tag_url = fill_tmpl(tag_name,page)
    # html=get_page(tag_url)
    # soup=BeautifulSoup(html,'html.parser')
    ul=soup.find('ul',{'class':{'feedlist_mod python'}})   
    # ul = list_div.find('ul',{'class':{'entry-list'}})
    # ul_in_div = ul.find('div')
    items = ul.find_all(recursive=False)
    for li in items:
        try:
            a = li.find('h2').find('a')
            recipe_url.append( a['href'])
        except:
            continue
    driver.quit()
    return recipe_url

def get_info(url,cate):  
    html= get_page(url)
    # doc = pq(html)
    soup=BeautifulSoup(html,'html.parser')
    title=soup.find('h1',{'class':{'title-article'}}).text.strip()  #title 
    author_div= soup.find('div',{'class':{'bar-content'}})  #作者名称
    author = author_div.find('a').text.strip()
    time = soup.find('span',{'class':{'time'}}).text.strip()
    # time = date['datetime']
    content = []
    bscontent_div = soup.find('div',{'id':{'content_views'}})
    bscontent = bscontent_div.find_all(recursive=False)
    # content_div=doc('.article.article-content')
    # soup.find_all('div',{'class':{'article fmt article-content'}})
    for element in bscontent:
        if element.name.startswith('h') :
            if element.text != '':
                content.append({
                    'ctype':'head',
                    'data': element.text
                })
        elif element.name == 'ol':
            content.append({
                'ctype':'p',
                'data': element.text
            })   
        elif element.name == 'p':
            if element.text != '':
                content.append({
                    'ctype':'p',
                    'data': element.text
                })
            
            img = element.find('img')
            try:
                content.append({
                'ctype':'img',
                'data': img['src']
            })
            except: pass
        elif element.name == 'pre':
            content.append({
                'ctype':'code',
                'data': element.find('code').text
            })
        elif element.name == 'table':
            content.append({
                'ctype':'table',
                'data': element.text
            })
      
    dish_dict = {  
        "题目": title,
        "作者": author ,
        "发布时间":time,
        "内容":content,
    }
    print('{}--爬取完成！'.format(title))
    return dish_dict

def yes_or_no(item):  #判断是不是空的
    if not item:
        item='无'
    return item


if __name__ == '__main__':
    # print('正在爬取http://www.xicidaili.com/nn的前1页的ip代理')
    # get_proxy(2)  # 1页
    # print('第1页ip代理爬取以及检验完成，并存入useful_ip_proxy.txt文件中')
    start_url='https://segmentfault.com/tags'
    # tag_name=get_tag_name(start_url)
    for i in range(len(url_list)):
        print('开始爬取{}分类'.format(tag_name[i]))
        recipe_url=get_recipe_url(url_list[i])
        # dish_list = []
        for j in range(len(recipe_url)):
            try:
                dishinfo = get_info(recipe_url[j],tag_name[i])
                dishinfo['cate'] = tag_name[i]
                # print(dishinfo)
                # dish_list.append(dishinfo)
                with open('csdn.txt','a+',encoding='utf-8')as f:
                    json.dump(dishinfo,f,ensure_ascii=False)
                    f.write('\n')
                f.close()
                time.sleep(random.random()*30)
            except Exception as e:
                traceback.print_exc()
                # print('get info fail')
                time.sleep(random.random()*10)
                continue
        time.sleep(random.random()*30)
       