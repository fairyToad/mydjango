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

