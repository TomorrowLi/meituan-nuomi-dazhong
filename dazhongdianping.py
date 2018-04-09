#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/4/8 17:54
# @Author  : tomorrowli
import requests
from pyquery import PyQuery as pq
import json
import re
import pymongo
import MySQLdb
from _config import *
keyword='自助餐'
def get_url_city():
    url='http://www.dianping.com/citylist'
    headers={
        'User-Agent': 'Mozilla/5.0(Windows NT 10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/64.0.3282.186Safari/537.36' ,

    }
    response=requests.get(url,headers=headers)
    doc=pq(response.text)
    items=doc('.letter-item .terms .findHeight .link').items()
    for item in items:
        products={
            'city':item.text(),
            'city_url':item.attr('href')
        }
        get_url_city_id(products)
def get_url_city_id():
    url = 'https://www.dianping.com/ajax/citylist/getAllDomesticCity'
    headers = {
        'User-Agent': 'Mozilla/5.0(Windows NT 10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/64.0.3282.186Safari/537.36' ,

    }
    response = requests.get(url , headers=headers)
    data=json.loads(response.text)
    for i in range(1,35):
        url_data=data['cityMap'][str(i)]
        for item in url_data:
            product={
                'cityName':item['cityName'],
                'cityId':item['cityId'],
                'cityEnName':item['cityEnName']
            }
            get_url_keyword(product)
            break
def get_url_keyword(product):
    urls = 'https://www.dianping.com/search/keyword/{}/0_%{}'.format(product['cityId'], keyword)
    headers = {
        'User-Agent': 'Mozilla/5.0(Windows NT 10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/64.0.3282.186Safari/537.36' ,

    }
    response = requests.get(urls, headers=headers)
    req=r'data-hippo-type="shop" title=".*?" target="_blank" href="(.*?)"'
    data=re.findall(req,response.text)
    for url in data:
        get_url_data(url)
def get_url_data(url):
    headers= {
        'User-Agent': 'Mozilla/5.0(Windows NT 10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/64.0.3282.186Safari/537.36' ,
        'Host': 'www.dianping.com',
        'Pragma': 'no - cache',
        'Upgrade - Insecure - Requests': '1'
    }
    response = requests.get(url,headers=headers)
    doc=pq(response.text)
    title=doc('#basic-info > h1').text().replace('\n','').replace('\xa0','')
    avgPriceTitle=doc('#avgPriceTitle').text()
    taste=doc('#comment_score > span:nth-of-type(1)').text()
    Environmental=doc('#comment_score > span:nth-of-type(2)').text()
    service=doc('#comment_score > span:nth-of-type(3)').text()
    street_address=doc('#basic-info > div.expand-info.address > span.item').text()
    tel=doc('#basic-info > p > span.item').text()
    info_name=doc('#basic-info > div.promosearch-wrapper > p > span').text()
    time=doc('#basic-info > div.other.J-other > p:nth-of-type(1) > span.item').text()
    product={
        'title':title,
        'avgPriceTitle':avgPriceTitle,
        'taste': taste ,
        'Environmental':Environmental,
        'service': service ,
        'street_address':street_address,
        'tel': tel ,
        'info_name':info_name,
        'time':time
    }
    save_mysql(product)
def save_mysql(product):
    conn=MySQLdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASSWORD,MYSQL_DB,chatset='utf-8')
    cursor=conn.cursor()
    cursor.execute("insert into dazhong(title,avgPriceTitle,taste,Environmental,service,street_address,tel,info_name,time) values('{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(product['title'],product['avgPriceTitle'],product['taste'],product['Environmental'],product['service'],product['street_address'],product['tel'],product['info_name'],product['time']))
    print('成功存入数据库' , product)
def save_mogodb(product):
    client=pymongo.MongoClient(MOGO_URL)
    db=client[MOGO_DB_D]
    try:
        if db[MOGO_TABLE_D].insert(product):
            print('保存成功',product)
    except Exception:
        print('保存失败',product)
def main():
    get_url_city_id()
if __name__ == '__main__':
    main()