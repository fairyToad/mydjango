import redis

#定义地址和端口
host = '127.0.0.1'
port = 6379

#建立redis连接
r = redis.Redis(host=host,port=port)

#声明一个值
r.set('test','123')

#取值
code = r.get('test')

#转码
code = code.decode('utf-8')

print(code)