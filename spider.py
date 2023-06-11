#导入库
import requests
from bs4 import BeautifulSoup
import time
import sys
from datetime import date
import json
import pandas as pd
from lxml import etree
# 定义函数，用来处理User-Agent和Cookie
def ua_ck():
    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
    #运用浏览器工具捕获cokkies，便于之后拓展操作
    cookies = 'bid=k76etST2aiE; ll="118318"; __utmc=30149280; apiKey=; _pk_id.100001.2fad=62ce42d4dd3e2bdb.1685972252.; last_login_way=qrcode; push_noty_num=0; push_doumail_num=0; ap_v=0,6.0; __utma=30149280.280268441.1681819070.1686279796.1686281954.7; __utmb=30149280.0.10.1686281954; __utmz=30149280.1686281954.7.4.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __gads=ID=fd1bd604e72d503f-2251145233df0039:T=1681819068:RT=1686283148:S=ALNI_MZQBVbL4oM9sG3ZbRketsO91zojqQ; __gpi=UID=00000bf7bc33c594:T=1681819068:RT=1686283148:S=ALNI_MZjXcqp2ZVo6J_RquPev4adJi_WmQ; _pk_ref.100001.2fad=%5B%22%22%2C%22%22%2C1686283162%2C%22https%3A%2F%2Fmovie.douban.com%2Ftop250%22%5D; _pk_ses.100001.2fad=1; dbcl2="271182699:smYdoc153wo"; ck=xOWN'
    # Cookie转化为字典
    cookies = cookies.split('; ')
    cookies_dict = {}
    for i in cookies:
        cookies_dict[i.split('=')[0]] = i.split('=')[1]
    #遍历cookies字典，将每个元素按‘=’分割为键值对
    return user_agent, cookies_dict

# 定义函数，用于获取豆瓣top250每一个页面的网址
def get_urls(n):
    urls = []  # 用于存放网址
    num = (n-1)*25+1
    for i in range(0, num, 25):
        url = 'https://movie.douban.com/top250?start={}&filter='.format(i)#构造页面连接
        urls.append(url)

    return urls

# 定义函数，获取每个页面25部电影的链接
def get_movies_url(url, u_a, c_d):
    '''
    url：每一个页面的链接
    u_a：User-Agent
    c_d：cookies
    '''

    html = requests.get(url,
                        headers=u_a,  # 加载User-Agent
                        cookies=c_d)  # 加载cookie

    html.encoding = html.apparent_encoding  
    print(html)
    #使用 apparent_encoding 属性来获取解析后的表面编码，并将其赋值给 html.encoding 属性，以确保正确地解析网页内容。
    soup = BeautifulSoup(html.text, 'html.parser')  # 用 html.parser 来解析网页
    items = soup.find('ol', class_='grid_view').find_all('li')
    movies_url = []
    for item in items:
        # 电影链接
        movie_href = item.find('div', class_='hd').find('a')['href']
        movies_url.append(movie_href)

    return movies_url
    time.sleep(0.4)    # 设置时间间隔，0.4秒采集一次，避免频繁登录网页

# 定义函数，获取每一部电影的详细信息
def get_movie_info(href, u_a, c_d):
    html = requests.get(href,
                        headers=u_a,
                        cookies=c_d)
    soup = BeautifulSoup(html.text, 'html.parser')  # 用 html.parser 来解析网页
    item = soup.find('div', id='content')
    movie = {}  # 新建字典，存放电影信息
    movie['电影标题'] = item.h1.span.text
    #导演、类型、制片国家/地区、语言、上映时间、片长
    
    movie['电影其他信息'] = item.find(
        'div', id='info').text.replace(' ', '').split('\n')
    
    #通过筛选：的方式自动分割出
    # for i in movie['电影其他信息']:
    #     if ':' in i:
    #         movie[i.split(':')[0]] = i.split(':')[1]
    #     else:
    #         continue
    # # 豆瓣评分、评分人数
    movie['评分'] = item.find('div', id='interest_sectl').find(
        'div', class_='rating_self clearfix').find('strong', class_='ll rating_num').text
    movie['评分人数'] = item.find('div', id='interest_sectl').find('div', class_='rating_self clearfix').find(
        'div', class_='rating_sum').find('span', property='v:votes').text
    movie['评论id'] = item.find('span',class_='comment-info').find('a').text
    movie['评论时间']=item.find('span',class_='comment-info').find('span',class_='comment-time').text
    movie['评论内容']=item.find('div',class_='comment').find('span',class_='short').text
    movie['评分']=item.find('span',class_='comment-info').find_all('span')[1].get('title')
    time.sleep(0.4)  # 0.4秒采集一次，避免频繁登录网页
    name = movie['电影标题']
    print(f'完成采集{name}')
    return movie
    

# 设置主函数，运行上面设置好的函数
def main():
    n = 1
    # 处理User-Agent和Cookie
    login = ua_ck()
    u_a = login[0]
    c_d = login[1]
    # 获取每一页的链接
    urls = get_urls(n)
    print('成功获取页面')

    # 获取每一页电影的链接
    top250_urls = []
    for url in urls:
        result = get_movies_url(url, u_a, c_d)
        top250_urls.extend(result)
    print('开始爬取详细信息')
    # 获取每一部电影的详细信息
    top250_movie = []  # 储存每部电影的信息
    error_href = []  # 储存采集错误的网址
    for href in top250_urls[:]:
        try:
            movie = get_movie_info(href, u_a, c_d)
            top250_movie.append(movie)
        except:
            #排除错误信息
            error_href.append(href)
            print('采集失败，失败网址是{}'.format(href))

    print('电影详细信息采集完成！！总共采集{}条数据'.format(len(top250_movie)))
    return top250_movie, error_href

# 启动主函数，开始采集数据
result = main()
print(result)
with open("data_file.json", "w",encoding='utf-8') as fp:
    json.dump(result,fp=fp,ensure_ascii=False)
