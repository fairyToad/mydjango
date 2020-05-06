from django.shortcuts import render,redirect
#导包
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
#导入类视图
from django.views import View

import json
from django.core.serializers import serialize
from rest_framework.response import Response
from rest_framework.views import APIView
#导入加密库
import hashlib
#导入图片库
#绘画库
from PIL import ImageDraw
#字体库
from PIL import ImageFont
#图片库
from PIL import Image
#随机库
import random
#文件流
import io

import requests

#导入上传文件夹配置
from mydjango.settings import UPLOAD_ROOT
import os
# 文件改名
from datetime import datetime

# 压缩文件
import cv2

#导入原生sql模块
from django.db import connection

import jwt

#导入redis数据库
import redis

#导入时间模块
import time

#导入公共目录变量
from mydjango.settings import BASE_DIR

#导包
from django.db.models import Q,F

#导入dwebsocket的库
from dwebsocket.decorators import accept_websocket
import uuid

from myapp.models import User


# 建立redis链接
#定义ip和端口
host = "localhost"
port = 6379
#建立链接
r = redis.Redis(host=host,port=port)

#七牛云token
from qiniu import Auth
class QiNiu(APIView):
	def get(self,request):
		#声明认证对象
		q = Auth('E2IZM3koC1GR1DUqJHactmixzdyZZhx0edBKqDsk','GDnMkvRoE_kFhCSuvdqQj0VcNsRDOHzYJJ_bVd0_')
		#获取token
		token = q.upload_token('upload1907rgzn')
		return Response({'token':token})

#又拍云存储
import upyun
class UpYun(APIView):

	def post(self,request):

		#获取文件
		file = request.FILES.get('file')
		#新建又拍云实例
		up = upyun.UpYun('123123123123','test123456','ihw5JZsdxHD0PFVUqDsd2MFCQd4o8lIu')
		#声明头部信息
		headers = {'x-gmkerl-rotate':'auto'}

		#上传图片
		for chunk in file.chunks():
			res = up.put('/touxiang_test1.jpg',chunk,checksum=True,headers=headers)

		return Response({'filename':file.name})


#新浪微博回调方法
def wb_back(request):
	#接收参数
	code = request.GET.get('code',None)

	#定义token接口地址
	url = "https://api.weibo.com/oauth2/access_token"

	#定义参数
	re = requests.post(url,data={
		"client_id":"670240910", 
		# 密钥
		"client_secret":"bcd1f44a4b172290bcc942f019da7c80",
		# 认证类型(写死)
		"grant_type":"authorization_code",
		"code":code,
		# 回调网址 
		"redirect_uri":"http://127.0.0.1:8000/md_admin/weibo"
	})
	# 打印返回值 (通过token换取昵称)
	print(re.json()) 
	

	#换取新浪微博用户昵称
	res = requests.get('https://api.weibo.com/2/users/show.json',params={'access_token':re.json()['access_token'],'uid':re.json()['uid']})

	print(res.json())

	sina_id = ''
	user_id = ''

	#判断是否用新浪微博登录过(避免二次入库 )
	user = User.objects.filter(username=str(res.json()['name'])).first()

	if user:
		#代表曾经用该账号登录过
		sina_id = user.username
		user_id = user.id
	else:
		#首次登录，入库新浪微博账号
		user = User(username=str(res.json()['name']),password='')
		user.save()
		user = User.objects.filter(username=str(res.json()['name'])).first()
		sina_id = user.username
		user_id = user.id

	print(sina_id,user_id)

	#重定向
	return redirect("http://localhost:8080?sina_id="+str(sina_id)+"&uid="+str(user_id))
	# return HttpResponse("回调成功") 


# #文件上传通用类
class UploadFile(APIView):

	def post(self,request):

		#接收参数
		myfile = request.FILES.get('file')
		uid = request.POST.get("uid",None)
		
		# 获取后缀名
		ext = myfile.name.split('.')[-1]
		# 可以根据后缀判断文件格式是否合法
		# 拼接文件新名称
		filename = datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(100, 999)) + '.' + ext
             


		#建立文件流对象
		f = open(os.path.join(UPLOAD_ROOT,'',filename),'wb')
		#写入静态文件(后续压缩会将其覆盖)
		for chunk in myfile.chunks():
			f.write(chunk)
		f.close()

		# #图像压缩(jpg比png格式小)
		#将写入的原图读取出来
		img = cv2.imread(os.path.join(UPLOAD_ROOT,'',filename))
		#压缩成png格式 力度范围是0-9
		# cv2.imwrite('./snowgitlabk1.png',img,[cv2.IMWRITE_PNG_COMPRESSION,9])
		#压缩成jpg格式 力度范围0-100
		cv2.imwrite(os.path.join(UPLOAD_ROOT,'',filename),img,[cv2.IMWRITE_JPEG_QUALITY,20])


		# # 加水印(根据print的参数调整水印位置)
		# from PIL import Image,ImageDraw 
		# #读图
		# im = Image.open("./snowgitlabk.jpg")
		# # 输出一些文件的参数
		# print(im.format,im.size,im.mode)
		# #生成画笔
		# draw = ImageDraw.Draw(im)
		# #根据size参数绘制水印
		# draw.text((1900,670),'1907',fill = (76,234,124,180))
		# # 载入内存展示,尚未保存到本地
		# im.show()


		#根据前端传递的id修改头像地址(入库)
		user = User.objects.get(id=int(uid))
		user.img = filename
		user.save()

		return Response({'filename':filename})




#md5加密方法
def make_password(mypass):

	#生成md5对象
	md5 = hashlib.md5()

	#转码操作
	mypass_utf8 = str(mypass).encode(encoding="utf-8")

	#加密操作
	md5.update(mypass_utf8)

	#返回密文
	return md5.hexdigest()

#注册接口
class Register(APIView):

	def get(self,request):

		#接收参数
		username = request.GET.get('username',None)
		password = request.GET.get('password',None)
		phone = request.GET.get('phone',None)

		#排重操作
		user = User.objects.filter(username=username).first()

		if user:
			return Response({'code':403,'message':'该用户名已经存在'})

		#入库
		user = User(username=username,password=make_password(password),phone=phone)

		#保存结果
		user.save()

		return Response({'code':200,'message':'恭喜注册成功'})

	def post(self,request):

		#接收参数
		username = request.POST.get('username',None)
		password = request.POST.get('password',None)

		#排重操作
		user = User.objects.filter(username=username).first()

		if user:
			return Response({'code':403,'message':'该用户名已经存在'})

		#入库
		user = User(username=username,password=make_password(password))

		#保存结果
		user.save()

		return Response({'code':200,'message':'恭喜注册成功'})

# 登录接口
# 模糊回应(用户名或密码错误)
# 锁号和防止锁号(刷脸或手机验证码)
class Login(APIView):
	def get(self,request):
		# 接收参数
		username=request.GET.get('username',None)
		password=request.GET.get('password',None)
		code = request.GET.get('code', None)

		# 比对验证码
		redis_code = r.get("code")
		# 转码 str(redis_code,'utf-8')
		redis_code = str(redis_code,'utf-8')
		# 从session取值
		# session_code = request.session.get('code', None)
		print(redis_code)
		if code != redis_code:
			return Response({'code': 403, 'message': '您输入的验证码有误'})

        # 此锁定方法会报key类型错误......,去掉外层判断不报错,但是业务逻辑会有问题
		if r.llen(username)<6:
            #查询参数
			#.get只查一个,查不到会报错,在确保能查到数据的时候使用(用户登录之后),可以提高性能(根据索引查询)
			#.filter查所有
			# 此处查询条件是且的关系
			user=User.objects.filter(username=username,password=make_password(password)).first()

			if user:
				return Response({
					'code':200,
					'message':'登陆成功',
					# 可扩展性
					'uid':user.id,
					'username':user.username
				})
			else:
				r.lpush(username, 1)
				if r.llen(username) > 5:
					# 单位是秒
					r.expire(username, 30)
					return Response({
						'code': 403,
						'message': '账号已被锁定'
					# 	到此只是告知锁定,待定
					})

				return Response({
					'code':403,
					'message':'用户名或密码错误',
				})
		return Response({
			'code':403,
			'message':'账号已被锁定',
		})



# 自定义图片验证码
class MyCode(View):

	#定义rgb随机颜色
	def get_random_color(self):

		R = random.randrange(255)
		G = random.randrange(255)
		B = random.randrange(255)

		return (R,G,B)

	#定义图片视图
	def get(self,request):
		#画布
		img_size = (120,50)
		#定义图片对象
		image = Image.new('RGB',img_size,'white')
		#定义画笔
		draw = ImageDraw.Draw(image,'RGB')
		# source = '0123456789'
		source = '0123456789abcdefghijklmnopqrstuvwxyz'
		#接收容器
		code_str = ''
		#进入循环绘制
		for i in range(4):
			#获取字母颜色
			text_color = self.get_random_color()
			#获取随机下标
			tmp_num = random.randrange(len(source))
			#随机字符串
			random_str = source[tmp_num]
			#装入容器
			code_str += random_str
			#绘制字符串
			draw.text((10+30*i,20),random_str,text_color)
		#获取缓存区
		buf = io.BytesIO()
		#将临时图片保存到缓冲
		image.save(buf,'png')
		#保存随机码
		r.set('code',code_str)
		print(r.get('code'))

		return HttpResponse(buf.getvalue(),'image/png')
