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


# 自定义图片验证码

# 建立redis链接
#定义ip和端口
host = "localhost"
port = 6379
#建立链接
r = redis.Redis(host=host,port=port)

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
