import random
import threading

import requests
from bs4 import BeautifulSoup
import os
import json 
import time
import random

import traceback


base_url = 'https://m.meishij.net/'


def get_page(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'}
    r = requests.get(url,headers = headers)
    r.encoding = 'utf-8'
    return r.text


def get_cate(url):  #得到所有的分类
    cate_url=[]
    cate_name=[]
    html=get_page(url)
    soup=BeautifulSoup(html,'html.parser')
    all_div=soup.find('div',{'class':{'category_box mt20'}})
    all_big_cate =all_div.find_all('div',{'class':{'category_sub clear'}})
    for big_div in all_big_cate:
        big_cate = big_div.find('h3').text
        small_cate_a = big_div.find_all('a',{'target':{'_blank'}})
        for sub_a in small_cate_a:
            small_cate=sub_a.text.strip()
            cate= big_cate+'_'+small_cate
            sub_href=sub_a['href']
            cate_url.append(sub_href)
            cate_name.append(cate)
    return cate_url,cate_name

def get_recipe_url(url):  #得到每个类别里面至少10页的上面所有菜谱的网址
    recipe_url=[]
    for i in range(1,10):
        try:
            url_t=url+'page/'+str(i) + '/'
            html=get_page(url_t)
            soup=BeautifulSoup(html,'html.parser')
            info=soup.find('div',{'class':{'ui_newlist_1 get_num'}})
            all_h2 = info.find_all('h2')
            # all_p=info.find_all('p',{'class':{'name'}})
            for h2 in all_h2:
                a = h2.find('a',{'target':{'_blank'}})
                href=a['href']
                recipe_url.append(href)
        except:
            continue
    return recipe_url

def get_info(url,cate):  #得到每道菜谱的详细信息
    html=get_page(url)
    soup=BeautifulSoup(html,'html.parser')
    title_h=soup.find('h1',{'class':{'recipe_De_title'}})  #菜名
    title = title_h.find('a').text
    name_a=soup.find('a',{'class':{'uright'}})
    name = name_a.find('span').text  #作者名称
    yl=[]  #用料
    all_tr_div=soup.find_all('div',{'class':{'recipeCategory_sub_R clear'}})
    # print(all_tr)
    all_li = []
    for div in all_tr_div:
        all_li.extend(div.find_all('li'))
    for li in all_li:    
        yl_name=li.find_all('span')[0].text.replace("\n", "") 
        yl_unit=li.find_all('span')[1].text.replace("\n", "")
        if not yl_unit:
            yl_unit='适量'
        yl.append(yl_name+':'+yl_unit)
    # print(yl)
    steps=[]
    pic_url = []
    all_li_div=soup.find('div',{'class':{'recipeStep'}})
    # print(all_li_div)
    all_li = all_li_div.find_all('li')
    # print(all_li)
    for li_div in all_li:
        steps.append(li_div.find('div',{'class':{'recipeStep_word'}}).text)
        image_div = li_div.find('div',{'class':{'recipeStep_img'}})
        image = image_div.find('img')
        try:
            pic_url.append(image['src'])
        except:
            continue
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
    start_url='https://home.meishichina.com/recipe-type.html'
    cate_url, cate_name=get_cate(start_url)
    for i in range(len(cate_url)):
        print('开始爬取{}分类'.format(cate_name[i]))
        recipe_url=get_recipe_url(cate_url[i])
        # dish_list = []
        for j in range(len(recipe_url)):
            try:
                dishinfo = get_info(recipe_url[j],cate_name[i])
                # print(dishinfo)
                # dish_list.append(dishinfo)
                with open('meishitianxia.txt','a+',encoding='utf-8')as f:
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
       