

import cv2
import requests
import base64
import urllib
#获取token
res=requests.get('https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=BmHDGvoW8pXOSgqc06GUSyx2&client_secret=d8uVL2nkdUUCrLrM0AAv6IenA49voxId')

token = res.json()['access_token']

#开始智能识图

#接口地址
url = 'https://aip.baidubce.com/rest/2.0/ocr/v1/webimage?access_token='+token
#定义头部信息
myheaders = {'Content-Type':'application/x-www-form-urlencoded'}


#读图,将原图去色
img = cv2.imread('./md.png',cv2.IMREAD_GRAYSCALE)
#写图(保护原图)
cv2.imwrite('./md1.png',img)

#操作图片
#读取图片
myimg = open('./md1.png','rb')
temp_img = myimg.read()
myimg.close()

#进行base64编码
temp_data = {'image':base64.b64encode(temp_img)}

#对图片地址进行urlencode操作
temp_data = urllib.parse.urlencode(temp_data)

#请求视图接口
res = requests.post(url=url,data=temp_data,headers=myheaders)
obj = res.json()['words_result']
print(obj)
code=''
for i in obj:
    code=code + i['words']
print(code)





# code = str(code).replace(' ','')
#
# print(code)



