#导入http库
import requests

url = 'http://localhost:8000/register/'

#定义参数
data = {'username':'123','password':'123'}

#发送请求
r = requests.get(url,params=data)

print(r.content.decode("utf-8"))