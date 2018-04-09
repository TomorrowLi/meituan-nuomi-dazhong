#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/4/2 17:02
# @Author  : tomorrowli

import requests
from pyquery import PyQuery as pq
import re
import json
from _config import *
import MySQLdb
import pymongo
keyword='自助餐'
def get_city():
    url='http://www.meituan.com/changecity/'
    response=requests.get(url)
    response.encoding='utf-8'
    doc=pq(response.text)
    items=doc('.city-area .cities .city').items()
    for item in items:
        product={
            'url':'http:'+item.attr('href'),
            'city':item.text()
        }
        get_url_number(product['url'])
def get_url(url):
    try:
        urls=url+'/s/'+keyword
        headers={
            'User-Agent': 'Mozilla/5.0(Windows NT 10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/64.0.3282.186Safari/537.36',
            'Host':'as.meituan.com',
            'Referer': 'http://as.meituan.com/',
            'Upgrade - Insecure - Requests': '1'
        }
        response=requests.get(urls,headers=headers)
        print(response.status_code)
        req=re.findall('no-search-content',response.text,re.S)
        print(response.text)
        print(req)
        if len(req)==0:
            print(response.text)
            req=r'<div class="default-list-item clearfix"><a href="(.*?)"'
            url_pase=re.findall(req,response.text,re.S)
            print(url_pase)
            for url in url_pase:
                print(url)
                # get_prase(url)
        else:
            print('对不起，没有符合条件的商家')
    except Exception:
        return None
def get_url_number(url):
    try:
        response=requests.get(url)
        req=r'{"currentCity":{"id":(.*?),"name":".*?","pinyin":'
        number_url=re.findall(req,response.text)
        for code in range(0,500,32):
            url='http://apimobile.meituan.com/group/v4/poi/pcsearch/{}?limit=32&offset={}&q={}'.format(number_url[0],code,keyword)
            response=requests.get(url)
            data=json.loads(response.text)
            imageUrl=data['data']['searchResult'][0]['imageUrl']
            address=data['data']['searchResult'][0]['address']
            lowestprice=data['data']['searchResult'][0]['lowestprice']
            title=data['data']['searchResult'][0]['title']
            url_id=data['data']['searchResult'][0]['id']
            product={
                'url_id':url_id,
                'imageUrl':imageUrl,
                'address':address,
                'lowestprice':lowestprice,
                'title':title
            }
            save_mysql(product)
    except Exception:
        return None

def get_prase(url):
    urls='http:'+url
    header = {
        'User-Agent': 'Mozilla/5.0(Windows NT 10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/64.0.3282.186Safari/537.36',
    }
    response=requests.get(urls,headers=header)
    print(response.text)
    req=r'"detailInfo":{"poiId":.*?,"name":"(.*?)","avgScore":(.*?),"address":"(.*?)","phone":"(.*?)","openTime":"(.*?)",'
    product=re.findall(req,response.text)
    products={
        'name':product[0][0],
        'avgScore':product[0][1],
        'address':product[0][2],
        'phone':product[0][3],
        'openTime': product[0][4],
    }
    print(products)
def save_mysql(product):
    conn=MySQLdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASSWORD,MYSQL_DB,charset='utf8')
    cursor = conn.cursor()
    cursor.execute("insert into meituan(url_id,imageUrl,address,lowestprice,title) values('{}','{}','{}','{}','{}')".format(product['url_id'], product['imageUrl'], product['address'], product['lowestprice'], product['title']))
    print('成功存入数据库',product)
def save_mongodb(result):
    client=pymongo.MongoClient(MOGO_URL)
    db=client[MOGO_DB_M]
    try:
        if db[MOGO_TABLE_M].insert(result):
            print('保存成功',result)
    except Exception:
        print('保存失败',result)
def main():
    get_city()
if __name__ == '__main__':
    main()