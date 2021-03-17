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


urlTmpl = Template(
    'https://segmentfault.com/t/${tagId}/blogs?page=${page}')
base_url = 'https://segmentfault.com/'

def fill_tmpl(self,tag,page):
    return self.urlTmpl.substitute(
        page=page, tagId=tag)


def get_page(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'}
    r = requests.get(url,headers = headers)
    return r.text


def get_tag_name(url):  #得到所有的分类
    html=get_page(url)
    soup=BeautifulSoup(html,'html.parser')
    all_tag_li=soup.find_all('li',{'class':{'tagPopup'}})
    tag_name = []
    for li in all_tag_li:
        big_cate = li.find('a').text.strip()
        # big_url= fill_tmpl(big_cate)
        tag_name.append(big_cate)
    return tag_name

def get_recipe_url(tag_name):  #得到每个类别里面所有页的上面的blogs
    recipe_url=[]
    page = 1
    tag_url = fill_tmpl(tag_name,page)
    html=get_page(url_t)
    soup=BeautifulSoup(html,'html.parser')
    list_div=soup.find('div',{'class':{'stream-list blog-stream'}})   
    items = list_div.find_all('div',{'class':{'summary'}})
    while len(items)>0:
        for item in items:
            h2 = item.find('h2')
            href= base_url + h2.find('a').['href']
            recipe_url.append(href)
        page = page+1
        tag_url = fill_tmpl(tag_name,page)
        html=get_page(url_t)
        soup=BeautifulSoup(html,'html.parser')
        list_div=soup.find('div',{'class':{'stream-list blog-stream'}})   
        items = list_div.find_all('div',{'class':{'summary'}})
        
    return recipe_url

def get_info(url,cate):  #得到每道菜谱的详细信息
    html=get_page(url)
    soup=BeautifulSoup(html,'html.parser')
    title=soup.find('h1').text.strip()  #菜名
    name=soup.find('span',{'class':{'posttime'}}).text.split(' ')[1]  #作者名称
    yl=[]  #用料
    all_tr_div=soup.find_all('div',{'class':{'c_mtr_li'}})
    # print(all_tr)
    for div in all_tr_div:
        yl_name=div.find_all('span')[0].text 
        yl_unit=div.find_all('span')[1].text
        if not yl_unit:
            yl_unit='适量'
        yl.append(yl_name+':'+yl_unit)
    # print(yl)
    steps=[]
    pic_url = []
    all_li_div=soup.find_all('div',{'class':{'stepitem'}})
    # print(all_li_div)
    # all_li = all_li_div[0].find_all('li')
    # print(all_li)
    for li_div in all_li_div:
        step_div = li_div.find_all('div',{'class':{'stepc'}})
        try:
            steps.append(step_div[0]('p')[0].text.strip())
        except:
            pass
        image = li_div.findAll('img',{'class':{'stepimg'}})
        try:
            pic_url.append(image[0]['src'])
        except:
            continue
    
    # print(pic_url)
    # print(steps)
    name=yes_or_no(name)
    yl=yes_or_no(yl)
    steps=yes_or_no(steps)
    # save_recipe(title,ratingValue,cooked,name,yl,steps,tip,cate,pic_url)
    dish_dict = {  
        "菜名": title,
        "这道菜的原作者":name,
        "用料":yl,
        "步骤":steps,
        "图片":pic_url,
    }
    print('{}--{}爬取完成！'.format(cate,title))
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
    tag_name=get_tag_name(start_url)
    for i in range(len(tag_name)):
        print('开始爬取{}分类'.format(tag_name[i]))
        recipe_url=get_recipe_url(tag_name[i]))
        # dish_list = []
        for j in range(len(recipe_url)):
            try:
                dishinfo = get_info(recipe_url[j],tag_name[i])
                dishinfo['cate'] = tag_name[i]
                # print(dishinfo)
                # dish_list.append(dishinfo)
                with open('sf.txt','a+',encoding='utf-8')as f:
                    json.dump(dishinfo,f,ensure_ascii=False)
                    f.write('\n')
                f.close()
                time.sleep(random.random()*10)
            except Exception as e:
                traceback.print_exc()
                # print('get info fail')
                time.sleep(random.random()*5)
                continue
        # big_cate=cate_name[i].split('_')[0]
        # small_cate=cate_name[i].split('_')[1]
        # path='./'+big_cate+'/'
        # if not os.path.exists(path):
        #     os.makedirs(path)
        # path_name=path+small_cate+'.json'
       