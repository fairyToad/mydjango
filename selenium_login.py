from selenium import webdriver
from selenium.webdriver import ActionChains
import time
import cv2
import requests
import base64
import urllib
#获取token
res=requests.get('https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=BmHDGvoW8pXOSgqc06GUSyx2&client_secret=d8uVL2nkdUUCrLrM0AAv6IenA49voxId')
token = res.json()['access_token']

#智能识图接口地址
url = 'https://aip.baidubce.com/rest/2.0/ocr/v1/webimage?access_token='+token
#定义头部信息
myheaders = {'Content-Type':'application/x-www-form-urlencoded'}



#建立浏览器实例
browser = webdriver.Chrome("d:/selenium/chromedriver.exe")

#打开网址
browser.get('http://localhost:8080/login')
time.sleep(2)
# 截大图
# browser.get_screenshot_as_file('md.png')
# 选取验证码图片
code_img = browser.find_element_by_class_name('imgcode')
# #只截取指定对象
code_img.screenshot("md.png")

#  截取的验证码图片不清晰,识别错误,想用下面的方法请求src,但是地址里有随机值,这种方法也行,暂且使用截屏
#  使用get_attribute()方法获取对应属性的属性值，src属性值就是图片地址。
# link = browser.find_element_by_class_name('imgcode').get_attribute('src')
# 通过requests发送一个get请求到图片地址，返回的响应就是图片内容
# r = requests.get(link)
# 将获取到的图片二进制流写入本地文件
# with open('md.png', 'wb') as f:
    # 对于图片类型的通过r.content方式访问响应内容，将响应内容写入md.png中
    # f.write(r.content)


#开始智能识图
# 获取验证码
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
#请求识图接口
res = requests.post(url=url,data=temp_data,headers=myheaders)
obj = res.json()['words_result']
# print(obj)
code=''
for i in obj:
    code=code + i['words']
print(code)



#群体选择器
browser.find_elements_by_tag_name('input')[1].send_keys('test')
browser.find_elements_by_tag_name('input')[2].send_keys('123')
browser.find_elements_by_tag_name('input')[3].send_keys(code)

#进行拖动操作
button = browser.find_element_by_class_name('dv_handler')
print(button)
#声明动作实例
action = ActionChains(browser)
#点击并且按住
action.click_and_hold(button).perform()
action.reset_actions()
#实际拖动像素和轨迹长度是有出入的
action.move_by_offset(280,0).perform()
#点击登录按钮
browser.find_element_by_class_name('h-btn').click()
#延迟等待
time.sleep(3)

#关闭浏览器
browser.close()