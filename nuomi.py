#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/4/2 17:03
# @Author  : tomorrowli

import requests
from pyquery import PyQuery as pq
from urllib.parse import urlencode
import re
import MySQLdb
import pymongo
from _config import *
keyword='自助餐'
def get_city():
    url='https://www.nuomi.com/pcindex/main/changecity'
    response=requests.get(url)
    response.encoding='utf-8'
    doc=pq(response.text)
    items=doc('.city-list .cities li').items()
    for item in items:
        product={
            'city':item.find('a').text(),
            'url':'https:'+item.find('a').attr('href')
        }
        get_pase(product['url'],keyword)
def get_pase(url,keyword):
    head={
        'k':keyword,
    }
    urls=url+'/search?'+urlencode(head)
    response=requests.get(urls)
    response.encoding = 'utf-8'
    req=re.findall('noresult-tip',response.text)
    if req:
        print('抱歉,没有找到你搜索的内容')
    else:
        req=r'<a href="(.*?)" target="_blank"><img src=".*?" class="shop-infoo-list-item-img" /></a>'
        url_req=re.findall(req,response.text)
        for i in url_req:
            url_pase='https:'+i
            get_pase_url(url_pase)
        req=r'<a href="(.*?)" .*? class="ui-pager-normal" .*?</a>'
        url_next=re.findall(req,response.text)
        for i in url_next:
            url_pases=url+i
            get_pase_url(url_pases)
def get_pase_url(url):
    response=requests.get(url)
    response.encoding = 'utf-8'
    doc=pq(response.text)
    product={
        'title':doc('.shop-box .shop-title').text(),
        'score':doc('body > div.main-container > div.shop-box > p > span.score').text(),
        'price':doc('.shop-info .price').text(),
        'location':doc('.item .detail-shop-address').text(),
        'phone':doc('body > div.main-container > div.shop-box > ul > li:nth-child(2) > p').text(),
        'time':doc('body > div.main-container > div.shop-box > ul > li:nth-child(3) > p').text(),
        'tuijian':doc('body > div.main-container > div.shop-box > ul > li:nth-child(4) > p').text()
    }
    print(product)
    save_mysql(product)
    #save_mongodb(product)
def save_mysql(product):
    conn=MySQLdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASSWORD,MYSQL_DB,charset='utf8')
    cursor = conn.cursor()
    cursor.execute("insert into nuomi(title,score,price,location,phone,time,tuijian) values('{}','{}','{}','{}','{}','{}','{}')".format(product['title'] , product['score'] , product['price'] , product['location'] , product['phone'] ,product['time'] , product['tuijian']))
    print('成功存入数据库',product)
def save_mongodb(result):
    client=pymongo.MongoClient(MOGO_URL)
    db=client[MOGO_DB]
    try:
        if db[MOGO_TABLE].insert(result):
            print('保存成功',result)
    except Exception:
        print('保存失败',result)
def main():
    get_city()
if __name__ == '__main__':
    main()