#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests
import json
import sys
import re
from bs4 import BeautifulSoup
import pymysql
from lxml import etree


reload(sys)
sys.setdefaultencoding( "utf-8" )

img_base_path='/Users/chanming/Desktop/msj/img/'

db = pymysql.connect(host = '127.0.0.1', port = 3306, user = 'json', passwd = '123456', db = 'meishij', charset="utf8")
cursor = db.cursor()

#校验菜肴是否被拉取
check_dish_sql = " SELECT COUNT(id) FROM dish where NAME='{}' "
#插入菜肴
dish_insert_sql = "INSERT INTO `meishij`.`dish`( `category_first`, `category_second`, `name`, `url`, `comment`, `tec`, `difficulty`, `num`, `taste`, `prepare_time`, `cook_time`, `skills`, `origin_url`,`finished_url`,`local_finished_url`,`msj_url`) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s)"

#插入作法
cook_dish_insert_sql = "INSERT INTO `meishij`.`cook_dish`( `dish_name`, `step_num`, `step_name`, `url`, `origin_url`) VALUES ( %s, %s, %s, %s, %s)"

dish_food_insert_sql = "INSERT INTO `meishij`.`dish_food`( `type`, `food_name`, `num`, `dish_name`) VALUES ( %s, %s, %s, %s)"



def crawl():
    start_url='https://www.meishij.net/china-food/caixi/'
    r=requests.get(start_url,verify=False)
    soup = BeautifulSoup(r.text,'lxml')
    category1List = soup.find_all("dl",class_='listnav_dl_style1')
    for category1 in category1List:
        #category1=category1List[0]
        #一级分类
        category1name=category1.find('dt').get_text()
        aList=category1.find_all('a')
        #二级分类
        # arrs=['川菜', '湘菜', '粤菜', '东北菜', '鲁菜', '浙菜', '苏菜', '清真菜', '闽菜', '沪菜', '京菜', '湖北菜', '徽菜', '豫菜', '西北菜', '云贵菜', '江西菜', '山西菜']
        for atag in aList:
            category2name=atag.get_text()
            # if category2name in arrs:
            #     continue
            if category2name !='其它菜':
                continue
            print "%s" % category1name,'%s' % category2name

            r_category=requests.get(atag['href'])
            soup_category=BeautifulSoup(r_category.text,'html.parser')
            page_total_dom=soup_category.select_one('input[name="lm"]')
            start_index=1
            if page_total_dom:
                page_text=page_total_dom.get_text()
                page_text_arr=re.findall(r'\d+',page_text)
            else :
                page_text_arr=[1]
            for pageIndex in range(56,int(page_text_arr[0])+1):
                page_url = atag['href']+'?&page='+str(pageIndex)
                print page_url
                r_page=requests.get(page_url)
                soup_page = BeautifulSoup(bs_preprocess(r_page.text),'lxml')
                dish_list = soup_page.select('div[class="listtyle1"]')
                for dish in dish_list:
                    a_dish=dish.find('a');
                    r_dish=requests.get( a_dish['href'],verify=False);
                    #r_dish=requests.get('http://www.meishij.net/zuofa/baochaopangxie.html');
                    soup_dish = BeautifulSoup(bs_preprocess(r_dish.text),'lxml')
                    print '\r\n'
                    print a_dish['href']
                    try:
                        name=soup_dish.select_one('a[id="tongji_title"]').get_text()
                    except Exception as e:
                        print '广告下一条'
                        continue
                    print("%s " % name)
                    #校验菜肴是否已被拉取
                    #name = 'liyuhang'
                    check_dish_sql_name = check_dish_sql.format(name)
                    cursor.execute(check_dish_sql_name)
                    count = cursor.fetchone()
                    if count[0]>=1:
                        continue
                    
                    db_dish={}
                    db_dish['msj_url']=a_dish['href']
                    db_dish['category_first']=category1name
                    db_dish['category_second']=category2name
                    db_dish['name'] = name

                    li_list=[]
                    li_sig=soup_dish.find('li',class_='w127')
                    li_list.append(li_sig)
                    li_sigList=li_sig.find_next_siblings('li')
                    li_list=li_list+li_sigList

                    #工艺
                    a_tec = li_list[0].find('a');
                    if a_tec:
                        tec = a_tec.get_text()
                    else:
                        tec = li_list[0].find('div').get_text()
                    #难度
                    a_difficulty = li_list[1].find('a')
                    if a_difficulty:
                        difficulty = a_difficulty.get_text()
                    else:
                        difficulty = li_list[1].find('div').get_text()
                    
                    #人数
                    a_num = li_list[2].find('a')
                    if a_num:
                        num = a_num.get_text()
                    else:
                        num = li_list[2].find('div').get_text()
                    #口味
                    a_taste = li_list[3].find('a')
                    if a_taste:
                        taste = a_taste.get_text()
                    else:
                        taste = li_list[3].find('div').get_text()
                    #准备时间
                    a_prepare_time = li_list[4].find('a')
                    if a_prepare_time:
                        prepare_time = a_prepare_time.get_text()
                    else:
                        prepare_time = li_list[4].find('div').get_text()
                    #烹饪时间
                    a_cook_time=li_list[5].find('a')
                    if a_cook_time:
                        cook_time = a_cook_time.get_text()
                    else:
                        cook_time = li_list[5].find('div').get_text()

                    swiper_list=soup_dish.find_all('div',class_='swiper-slide');
                    #swiper_list=swiper_list[1:-1]
                    furl_list=[]
                    flurl_list=[]
                    for swiper in swiper_list:
                        furl=swiper.find('img')['src']
                        fsurl=furl[furl.rfind('/')+1:]
                        f=open(img_base_path+fsurl,'wb')
                        img=requests.get(furl)
                        f.write(img.content)
                        f.close()
                        furl_list.append(furl)
                        flurl_list.append(fsurl)

                        
                    db_dish['tec']=tec
                    db_dish['difficulty']=difficulty
                    db_dish['num']=num
                    db_dish['taste']=taste
                    db_dish['prepare_time']=prepare_time
                    db_dish['cook_time']=cook_time
                    db_dish['finished_url']=",".join(s for s in furl_list)
                    db_dish['local_finished_url']=",".join(s for s in flurl_list )

                    if soup_dish.find('div',class_='materials'):
                        comment_p=soup_dish.find('div',class_='materials').find('p')
                        if comment_p:
                            db_dish['comment']=comment_p.get_text()
                        else:
                            db_dish['comment']=''
                    else:
                        db_dish['comment']=''

                    origin_url=soup_dish.find('div',class_='cp_headerimg_w').find('img')['src']
                    db_dish['origin_url']=origin_url
                    index=origin_url.rfind('/');
                    url=origin_url[index+1:]
                    db_dish['url'] = url

                    #下载图片
                    try:
                        f=open(img_base_path+url,'wb')
                        img=requests.get(origin_url)
                        f.write(img.content)
                        f.close()                    
                    except Exception  as e:
                        pass

                    liFlag=1
                    step_flag=soup_dish.find('em',class_='step')
                    if step_flag and step_flag.parent.name=='p':
                        liFlag=2
                    pp=soup_dish.select('em.step + img')
                    if pp:
                        liFlag=3

                    h2_title=soup_dish.find('h2',text='烹饪技巧')
                    try:
                        if h2_title:
                            if liFlag==2:
                                p_list=h2_title.find_next_siblings('p')
                                skill_list=[]
                                for p_skill in p_list:
                                    if p_skill.get_text()=='':
                                        continue
                                    skill_list.append(p_skill.get_text())
                                skills="|".join(s for s in skill_list)
                            else:
                                skills=h2_title.find_next_sibling('p').get_text()
                        else:
                            skills=''
                    except Exception as e:
                        skills=''

                    db_dish['skills'] = skills
                    cursor.execute(dish_insert_sql,(db_dish['category_first'],db_dish['category_second'],db_dish['name'],db_dish['url'],db_dish['comment'],db_dish['tec'],db_dish['difficulty'],db_dish['num'],db_dish['taste'],db_dish['prepare_time'],db_dish['cook_time'],db_dish['skills'],db_dish['origin_url'],db_dish['finished_url'],db_dish['local_finished_url'],db_dish['msj_url']))
                    db.commit()

                    if liFlag==2:
                        step_list=soup_dish.find_all('em',class_='step')
                        for step in step_list:
                            cook_dish={}
                            cook_dish['step_name']=step.parent.get_text()
                            cook_dish['step_num']=cook_dish['step_name'][0:cook_dish['step_name'].find('.')]
                            cook_dish['dish_name']=db_dish['name']
                            img_p=step.find_parent().find_next_sibling('p')
                            if img_p:
                                step_img=img_p.find('img')
                                if step_img:
                                    cook_dish['origin_url']=step_img['src']
                                    cook_dish['url']=cook_dish['origin_url'][cook_dish['origin_url'].rfind('/')+1:]
                                    f=open(img_base_path+cook_dish['url'],'wb')
                                    img=requests.get(cook_dish['origin_url'])
                                    f.write(img.content)
                                    f.close()
                                else:
                                    cook_dish['origin_url']=''
                                    cook_dish['url']=''
                            else:
                                cook_dish['origin_url']=''
                                cook_dish['url']=''

                            cursor.execute(cook_dish_insert_sql,(cook_dish['dish_name'],cook_dish['step_num'],cook_dish['step_name'],cook_dish['url'],cook_dish['origin_url']))
                            db.commit()
                    elif liFlag==3:
                        step_list=soup_dish.find_all('em',class_='step')
                        for step in step_list:
                            cook_dish={}
                            cook_dish['step_name']=step.parent.get_text()
                            cook_dish['step_num']=cook_dish['step_name'][0:cook_dish['step_name'].find('.')]
                            cook_dish['dish_name']=db_dish['name'] 
                            step_img=step.find_next_sibling('img')
                            if step_img:
                                cook_dish['origin_url']=step_img['src']
                                cook_dish['url']=cook_dish['origin_url'][cook_dish['origin_url'].rfind('/')+1:]
                                f=open(img_base_path+cook_dish['url'],'wb')
                                img=requests.get(cook_dish['origin_url'])
                                f.write(img.content)
                                f.close()
                            else :
                                cook_dish['origin_url']=''
                                cook_dish['url']=''
                            cursor.execute(cook_dish_insert_sql,(cook_dish['dish_name'],cook_dish['step_num'],cook_dish['step_name'],cook_dish['url'],cook_dish['origin_url']))
                            db.commit()                            
                        pass
                    else:
                        step_list=soup_dish.find_all('div',class_='content clearfix')
                        for step in step_list:
                            cook_dish={}
                            cook_dish['step_name']=step.get_text()
                            cook_dish['step_num']=cook_dish['step_name'][0:cook_dish['step_name'].find('.')]
                            cook_dish['dish_name']=db_dish['name']

                            try:
                                cook_dish['origin_url']=step.find('img')['src']
                                cook_dish['url']=cook_dish['origin_url'][cook_dish['origin_url'].rfind('/')+1:]
                                #下载图片
                                f=open(img_base_path+cook_dish['url'],'wb')
                                img=requests.get(cook_dish['origin_url'])
                                f.write(img.content)
                                f.close()
                            except Exception as e:
                                cook_dish['origin_url']=''
                                cook_dish['url']=''

                            cursor.execute(cook_dish_insert_sql,(cook_dish['dish_name'],cook_dish['step_num'],cook_dish['step_name'],cook_dish['url'],cook_dish['origin_url']))
                            db.commit()

                    #用料
                    zl_div=soup_dish.find('div',class_="yl zl clearfix")
                    if zl_div:
                        li_list=zl_div.find_all('li')
                        for zl_li in li_list:
                            dish_food={}
                            dish_food['type']='主料'
                            h4_d=zl_li.find('h4');
                            dish_food['food_name']=h4_d.find('a').get_text()
                            dish_food['num']=h4_d.find('span').get_text()
                            dish_food['dish_name']=db_dish['name']
                            cursor.execute(dish_food_insert_sql,(dish_food['type'],dish_food['food_name'],dish_food['num'],dish_food['dish_name']))
                            print '主料:'+dish_food['food_name']
                            db.commit()

                    #辅料
                    fl_div_list=soup_dish.find_all('div',class_="yl fuliao clearfix")
                    if fl_div_list:
                        for fl_div in fl_div_list:
                            a_label=fl_div.select_one('h3 a')
                            fl_list = fl_div.find_all('li')
                            for fl_li in fl_list:
                                dish_food={}
                                dish_food['type']=a_label.get_text()
                                dish_food['dish_name']=db_dish['name']
                                dish_food['food_name']=fl_li.find('h4').find('a').get_text()
                                dish_food['num']=fl_li.find('h4').find_next_sibling('span').get_text()
                                cursor.execute(dish_food_insert_sql,(dish_food['type'],dish_food['food_name'],dish_food['num'],dish_food['dish_name']))
                                db.commit()
                                print dish_food['type']+':'+dish_food['food_name']



        




def bs_preprocess(html):
     """remove distracting whitespaces and newline characters"""
     pat = re.compile('(^[\s]+)|([\s]+$)', re.MULTILINE)
     html = re.sub(pat, '', html)       # remove leading and trailing whitespaces
     html = re.sub('\n', ' ', html)     # convert newlines to spaces
                                        # this preserves newline delimiters
     html = re.sub('[\s]+<', '<', html) # remove whitespaces before opening tags
     html = re.sub('>[\s]+', '>', html) # remove whitespaces after closing tags
     return html

crawl()