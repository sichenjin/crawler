import random
import threading

import requests
from bs4 import BeautifulSoup
import os
import json 
import time
import random

import traceback


base_url = 'http://www.xiachufang.com'

def get_proxy(total_page):  #得到前20页的ip代理，并对其验证
    proxy_list = []
    for page in range(1,total_page):
        url='http://www.xicidaili.com/nn/{}'.format(page)
        headers={'user-agent':'Mozilla/5.0'}
        proxies = {  # 随便在网上找的一个高匿代理，以为这个地址爬多了，也被反爬了......
            'http': 'http://' + '124.235.135.210:80',
            'https': 'https://' + '124.235.135.210:80',
        }
        r=requests.get(url,headers=headers,proxies=proxies)
        print('正在爬取ip代理--->{}'.format(url))
        soup=BeautifulSoup(r.text,'html.parser')
        trs = soup.find('table', id='ip_list').find_all('tr')
        for tr in trs[1:]:
            tds = tr.find_all('td')
            ip = tds[1].text.strip()
            port = tds[2].text.strip()
            proxy = ip + ':' + port
            proxy_list.append(proxy)
    #多线程检测
    threads = []
    for proxy in proxy_list:
        thread = threading.Thread(target=thread_test_proxy, args=(proxy,))
        threads.append(thread)
        thread.start()
    for thread in threads:  # 阻塞主进程，等待所有子线程结束
        thread.join()

def thread_test_proxy(proxy):  #添加线程模式
    url = 'http://www.baidu.com/'
    headers = {'User-Agent': 'Mozilla/5.0', }
    proxies = {
        'http': 'http://' + proxy,
        'https': 'https://' + proxy
    }
    try:
        r=requests.get(url,headers=headers,proxies=proxies,timeout=2)
        if r.status_code == 200:
            print('{}该代理IP可用'.format(proxy))
            thread_write_proxy(proxy)
        #else:
            #print('{}该代理IP不可用'.format(proxy))
    except:
        #print('{}该代理IP无效'.format(proxy))
        pass

def thread_write_proxy(proxy):
    with open('useful_ip_proxy.txt','a+')as f:
        f.write(proxy+'\n')
    f.close()

def get_page(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'}
    r = requests.get(url,headers = headers)
    return r.text

    # useful_ip_proxy = []
    # with open('useful_ip_proxy.txt', 'r')as f:
    #     info = f.readlines()
    #     for line in info:
    #         res = line.split('\n')[0]
    #         useful_ip_proxy.append(res)
    # f.close()
    # try:
    #     proxy = random.choice(useful_ip_proxy)
    #     proxies = {
    #         'http': 'http://' + proxy,
    #         'https': 'https://' + proxy
    #     }

    #     r=requests.get(url,proxies=proxies,timeout=5)
    #     r.raise_for_status()
    #     #r.encoding=r.apparent_encoding
    #     return r.text

    # except Exception as e:
    #     proxy = random.choice(useful_ip_proxy)
    #     proxies = {
    #         'http': 'http://' + proxy,
    #         'https': 'https://' + proxy
    #     }
    #     r = requests.get(url, proxies=proxies, timeout=5)
    #     r.raise_for_status()
    #     # r.encoding=r.apparent_encoding
    #     return r.text

def get_cate(url):  #得到所有的分类
    cate_url=[]
    cate_name=[]
    html=get_page(url)
    soup=BeautifulSoup(html,'html.parser')
    all_div=soup.find_all('div',{'class':{'cates-list-all'}})
    for div in all_div:
        big_cate=div('h4')[0].text.strip()
        all_a=div.find_all('a',{'target':{'_blank'}})
        for a in all_a:
            small_cate=a.text.strip()
            cate=big_cate+'_'+small_cate
            href=a['href']
            cate_url.append(base_url+href)
            cate_name.append(cate)
    return cate_url,cate_name

def get_recipe_url(url):  #得到每个类别里面至少5页的上面所有菜谱的网址
    recipe_url=[]
    for i in range(1,10):
        try:
            url_t=url+'?page='+str(i)
            html=get_page(url_t)
            soup=BeautifulSoup(html,'html.parser')
            info=soup.find('div',{'class':{'normal-recipe-list'}})
            all_a = info.find_all('a',{'target':{'_blank'}})
            all_p=info.find_all('p',{'class':{'name'}})
            for p in all_p:
                href=p('a')[0]['href']
                url_t=base_url+href
                recipe_url.append(url_t)
        except:
            continue
    return recipe_url

def get_info(url,cate):  #得到每道菜谱的详细信息
    html=get_page(url)
    soup=BeautifulSoup(html,'html.parser')
    title=soup.find('h1',{'class':{'page-title'}}).text.strip()  #菜名
    # try:
    #     ratingValue=soup.find('span',{'itemprop':{'ratingValue'}}).text.strip() #评分
    # except:
    #     ratingValue=''
    try:
        div1=soup.find('div',{'class':{'cooked'}})
        cooked=div1('span')[0].text.strip()  #做过这道菜的人
    except:
        cooked = '无'
    namediv=soup.find('div',{'class':{'author'}})  #作者名称
    name = namediv.find('a')['title']
    yl=[]  #用料
    all_tr_div=soup.find_all('div',{'class':{'ings'}})
    all_tr = all_tr_div[0].find_all('tr')
    # print(all_tr)
    for tr in all_tr:
        yl_name=tr('td')[0].text.strip()
        yl_unit=tr('td')[1].text.strip()
        if not yl_unit:
            yl_unit='适量'
        yl.append(yl_name+':'+yl_unit)
    # print(yl)
    steps=[]
    pic_url = []
    all_li_div=soup.find_all('div',{'class':{'steps'}})
    # print(all_li_div)
    all_li = all_li_div[0].find_all('li')
    # print(all_li)
    for li in all_li:
        steps.append(li('p')[0].text.strip())
        image = li.findAll('img')
        try:
            pic_url.append(image[0]['src'])
        except:
            continue
    try:
        tip=soup.find('div',{'class':{'tip'}}).text.strip()   #小贴士
    except:
        tip=''
    # print(pic_url)
    # print(steps)
    # ratingValue=yes_or_no(ratingValue)
    cooked=yes_or_no(cooked)
    name=yes_or_no(name)
    yl=yes_or_no(yl)
    steps=yes_or_no(steps)
    tip=yes_or_no(tip)
    # save_recipe(title,ratingValue,cooked,name,yl,steps,tip,cate,pic_url)
    dish_dict = {  
        "菜名": title,
        # "综合评分":ratingValue,
        "做过的人数":cooked,
        "这道菜的原作者":name,
        "用料":yl,
        "步骤":steps,
        "注意点":tip,
        "图片":pic_url,
    }
    print('{}--{}爬取完成！'.format(cate,title))
    return dish_dict

def yes_or_no(item):  #判断是不是空的
    if not item:
        item='无'
    return item

def save_recipe(title,ratingValue,cooked,name,yl,steps,tip,cate,pic_url):  #保存菜谱信息
    big_cate=cate.split('_')[0]
    small_cate=cate.split('_')[1]
    path='./'+big_cate+'/'
    if not os.path.exists(path):
        os.makedirs(path)
    path_name=path+small_cate+'.txt'
    with open(path_name,'a+',encoding='utf-8')as f:
        f.write('菜名：'+title+'\n')
        f.write('综合评分：'+ratingValue+'\n')
        f.write('做过的人数：'+cooked+'\n')
        f.write('这道菜的原作者：'+name+'\n')
        f.write('用料：'+'\n')
        for item_yl in yl:
            f.write(item_yl+'   ')
        f.write('\n')
        f.write('步骤：' + '\n')
        for item_steps in steps:
            f.write(item_steps+'\n')
        f.write('注意点：'+tip+'\n')
        # f.write('(#^.^#)❤(#^.^#)❤(#^.^#)❤这道菜(#^.^#)❤(#^.^#)❤(#^.^#)❤完成啦~')
        f.write('\n\n')
    f.close()

if __name__ == '__main__':
    # print('正在爬取http://www.xicidaili.com/nn的前1页的ip代理')
    # get_proxy(2)  # 1页
    # print('第1页ip代理爬取以及检验完成，并存入useful_ip_proxy.txt文件中')
    start_url='http://www.xiachufang.com/category/'
    cate_url, cate_name=get_cate(start_url)
    for i in range(len(cate_url)):
        print('开始爬取{}分类'.format(cate_name[i]))
        recipe_url=get_recipe_url(cate_url[i])
        # dish_list = []
        for j in range(len(recipe_url)):
            try:
                dishinfo = get_info(recipe_url[j],cate_name[i])
                dishinfo['类别'] = cate_name[i]
                # print(dishinfo)
                # dish_list.append(dishinfo)
                with open('xiachufang.txt','a+',encoding='utf-8')as f:
                    json.dump(dishinfo,f,ensure_ascii=False)
                    f.write('\n')
                f.close()
                time.sleep(random.random()*15)
            except Exception as e:
                traceback.print_exc()
                # print('get info fail')
                time.sleep(random.random()*6)
                continue
        # big_cate=cate_name[i].split('_')[0]
        # small_cate=cate_name[i].split('_')[1]
        # path='./'+big_cate+'/'
        # if not os.path.exists(path):
        #     os.makedirs(path)
        # path_name=path+small_cate+'.json'
       