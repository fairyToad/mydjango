from django.shortcuts import render,redirect
#导包
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
#导入类视图
from django.views import View

from myapp.models import User
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
from myapp.myser import UserSer


#第二种序列化方式
def userinfo_json(request):

    #读取数据库
    users = User.objects.all()

    #序列化操作
    mylist = json.loads(serialize('json',users,ensure_ascii=False))

    #返回
    return JsonResponse(mylist,safe=False,json_dumps_params={'ensure_ascii':False})



#用户信息接口
class UserInfo(APIView):

    def get(self,request):

        #获取用户id
        uid = request.GET.get('uid')

        #读取数据库
        users = User.objects.filter(id=int(uid)).first()

        #进行序列化操作
        user_ser = UserSer(users)

        #进行返回
        return Response(user_ser.data)



#定义地址和端口
host = '127.0.0.1'
port = 6379

#建立redis连接
r = redis.Redis(host=host,port=port)




#用户更新接口
class UpdateUser(APIView):

    def get(self,request):

        #接收参数
        uid = request.GET.get("uid")
        img = request.GET.get("img")

        #查询用户
        user = User.objects.get(id=int(uid))

        #保存头像
        user.img = img
        user.save()

        return Response({'message':'修改成功'})

        


#七牛云密钥接口
from qiniu import Auth

class QiNiu(APIView):

    def get(self,request):

        #声明密钥对象
        q = Auth('E2IZM3koC1GR1DUqJHactmixzdyZZhx0edBKqDsk','GDnMkvRoE_kFhCSuvdqQj0VcNsRDOHzYJJ_bVd0_')
        #生成令牌
        token = q.upload_token('testupload123')

        return Response({'uptoken':token})


#上传文件视图类
class UploadFile(View):

    def post(self,request):

        #接收文件
        myfile = request.FILES.get("file")
        #建立文件流对象
        f = open(os.path.join(UPLOAD_ROOT,'',str(myfile.name).replace('"','')),'wb')
        #进行写文件
        for chunk in myfile.chunks():
            f.write(chunk)
        #关闭文件流
        f.close()
        #返回文件名
        return HttpResponse(json.dumps({'filename':str(myfile.name).replace('"','')},ensure_ascii=False),content_type='application/json')



import time
import hmac
import base64
from hashlib import sha256
import urllib

#构造钉钉回调方法
def ding_back(request):

    #获取code
    code = request.GET.get("code")

    t = time.time()
    #时间戳
    timestamp = str((int(round(t * 1000))))
    appSecret ='ly-AzMKMmCKQP3geaILT_An32kEfKO3HeOtApy5CgKwjytevVZC0WYsT2gxMB160'
    #构造签名
    signature = base64.b64encode(hmac.new(appSecret.encode('utf-8'),timestamp.encode('utf-8'), digestmod=sha256).digest())
    #请求接口，换取钉钉用户名
    payload = {'tmp_auth_code':code}
    headers = {'Content-Type': 'application/json'}
    res = requests.post('https://oapi.dingtalk.com/sns/getuserinfo_bycode?signature='+urllib.parse.quote(signature.decode("utf-8"))+"&timestamp="+timestamp+"&accessKey=dingoaukgkwqknzjvamdqh",data=json.dumps(payload),headers=headers)

    res_dict = json.loads(res.text)
    print(res_dict)
    return HttpResponse(res.text)

#新浪微博回调视图
def weibo_back(request):

    #获取code
    code = request.GET.get('code')

    #换取网址
    access_token_url = "https://api.weibo.com/oauth2/access_token"

    #发送请求进行换取
    re_dict = requests.post(
        access_token_url,
        data={
           "client_id": '2636039333',
        "client_secret": "4e2fbdb39432c31dc5c2f90be3afa5ce",
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://127.0.0.1:8000/md_admin/weibo"
        }
    )

    print(re_dict.text)

    #强转
    re_dict = re_dict.text
    re_dict = eval(re_dict)

    #判断是否用新浪登陆过
    user = User.objects.filter(username=str(re_dict['uid'])).first()

    sina_id = ''
    user_id = ''

    if user:
        #代表曾经登录过
        sina_id = user.username
        user_id = user.id
    else:
        #自动创建账号
        user = User(username=str(re_dict['uid']),password='',type=0)
        #保存
        user.save()

        #查询用户id
        user = User.objects.filter(username=str(re_dict['uid'])).first()

        sina_id = str(re_dict['uid'])
        user_id = user.id

    #跳转操作
    return redirect('http://localhost:8080?sina_id='+str(sina_id)+"&uid="+str(user_id))
    #return HttpResponse(re_dict['uid'])


#定义验证码
class MyCode(View):

    #定义随机验证颜色
    def get_random_color(self):
        R = random.randrange(255)
        G = random.randrange(255)
        B = random.randrange(255)

        return (R,G,B)

    #随机验证码
    def get(self,request):
        #画布
        img_size = (110,50)
        #定义颜色类型
        image = Image.new("RGB",img_size,'white')
        #画笔
        draw = ImageDraw.Draw(image,'RGB')
        #定义随机字符串
        source = '0123456789'
        #容器，用来接收随机字符串
        code_str = ''
        for i in range(4):
            #获取字体颜色
            text_color = self.get_random_color()
            #获取字符串
            tmp_num = random.randrange(len(source))
            #获取字符集
            random_str = source[tmp_num]
            #添加到容器中
            code_str += random_str
            #绘制
            draw.text((10+30*i,20),random_str,text_color)
        #文件流缓冲区
        buf = io.BytesIO()
        #将图片保存到缓冲区
        image.save(buf,'png')
        #将随机码存储到redis中
        r.set('code',code_str)
        #将验证码存储到session中
        request.session['code'] = code_str

        return HttpResponse(buf.getvalue(),'image/png')




#md5加密方法
def make_password(mypass):
    #生成md5对象
    md5 = hashlib.md5()
    #定义加密对象
    sign_str = mypass
    #转码
    sign_utf8 = str(sign_str).encode(encoding="utf-8")
    #加密操作
    md5.update(sign_utf8)
    #生成密文
    md5_server = md5.hexdigest()
    return md5_server


#登录接口
class Login(APIView):

    def get(self,request):

        #接收参数
        username = request.GET.get('username','未收到用户名')
        password = request.GET.get('password','未收到密码')

        #查询数据
        user = User.objects.filter(username=username,password=make_password(password)).first()

        if user:
            res = {}
            res['code'] = 200
            res['message'] = '登录成功'
            res['username'] = user.username
            res['uid'] = user.id
            return Response(res)
        else:
            res = {}
            res['code'] = 405
            res['message'] = '用户名或者密码错误'
            return Response(res)


#注册接口
class Register(APIView):

    def get(self,request):

        #接收参数
        username = request.GET.get('username','未收到用户名')
        password = request.GET.get('password','未收到密码')
        code = request.GET.get('code','未收到验证码')


        #从session中获取验证码
        session_code = request.session.get('code',None)

        print(session_code)

        #从redis中获取生成好的验证码
        mycode = r.get('code')
        #转码
        mycode = mycode.decode('utf-8')

        #print(mycode)

        #判断验证码是否输入正确
        if code != mycode:
            res = {}
            res['code'] = 405
            res['message'] = '验证码输入错误'
            return Response(res)

        #排重操作
        user = User.objects.filter(username=username).first()

        if user:
            res = {}
            res['code'] = 405
            res['message'] = '用户已经存在'
            return Response(res)

        #进行入库操作
        user = User(username=username,password=make_password(password),img='',type=0)
        #保存
        user.save()

        #返回结果
        res = {}
        res['code'] = 200
        res['message'] = '注册成功'
        return Response(res)


