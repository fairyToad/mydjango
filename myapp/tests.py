# from django.test import TestCase

# Create your tests here.
import jwt
import datetime
# 只能存在前端(cookie或webstorage)

payload={
    # 引入过期时间
    'exp':int((datetime.datetime.now() + datetime.timedelta(seconds=30)).timestamp()),

    'data':{'uid':2}
}


# 加密(载荷,密钥,加密算法)
# encode_jwt=jwt.encode(payload,'qwe123',algorithm='HS256')
# print(encode_jwt)
# #b'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1aWQiOiIyIn0.Ksi4a84mnenqiBuKSfhDE5P5l1aZ4-q_wNjuQHj0cf8'
# # 转码成字符串
# encode_str=str(encode_jwt,'utf-8')
# print(encode_str)
# eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1aWQiOiIyIn0.Ksi4a84mnenqiBuKSfhDE5P5l1aZ4-q_wNjuQHj0cf8
# 传给前端存储



# 前端请求敏感信息时,将此token携带返回
# 后端对其进行解密,并验证
# 解密
try:
    decode_jwt=jwt.decode('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1ODg4NDI3NzUsImRhdGEiOnsidWlkIjoyfX0.1Ihtvsx1NmSZX6Nx22mnBkVFLzkHCAaazydrZOV5rzg','qwe123',algorithms=['HS256'])
    print(decode_jwt)
    # {'uid': '2'}
    print(decode_jwt['data']['uid'])
    # 2
except Exception as e:
    print('guoqi')
    

