import requests
user_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}
# 发送GET请求并获取cookies
response = requests.get('https://movie.douban.com/top250',headers=user_agent)
cookies = response.cookies

# 打印cookies
print(cookies)