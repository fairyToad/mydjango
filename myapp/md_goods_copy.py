from django.shortcuts import render,redirect
#导包
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
#导入类视图
from django.views import View

from myapp.models import User,Goods,Category
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

#导入序列化对象
from myapp.myser import UserSer,GoodsSer,CategorySer

#定义地址和端口
host = '127.0.0.1'
port = 6379

#建立redis连接
r = redis.Redis(host=host,port=port)


#商品分类接口
class CategoryInfo(APIView):

    def get(self,request):

        #进行商品查询
        category = Category.objects.filter()

        #进行序列化操作
        cate_ser = CategorySer(category,many=True)

        #进行返回
        return Response(cate_ser.data)



#商品入库接口
class AddGoods(APIView):

    def get(self,request):

        name = request.GET.get('name')
        desc = request.GET.get('desc')
        img = request.GET.get('img')
        video = request.GET.get('video')
        param = request.GET.get('param')
        cid = request.GET.get('cid')
        price = request.GET.get('price')

        #排重
        goods = Goods.objects.filter(name=name).first()

        if goods:
            res = {}
            res['code'] = 405
            res['message'] = '该商品已经存在'
            return Response(res)

        #进行入库
        goods = Goods(name=name,desc=desc,img=img,video=video,param=param,cid=cid,price=price)
        goods.save()

        res = {}
        res['code'] = 200
        res['message'] = '商品添加成功'

        return Response(res)





#商品列表接口
class GoodsList(APIView):

    def get(self,request):

        #获取用户id
        uid = request.GET.get('uid')

        #读取数据库
        users = User.objects.filter(id=int(uid)).first()

        #进行序列化操作
        user_ser = UserSer(users)

        #进行返回
        return Response(user_ser.data)








