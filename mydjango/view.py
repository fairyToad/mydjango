from django.shortcuts import render,redirect
#导包
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
#导入类视图
from django.views import View
import requests
import hashlib
import xmltodict
#from myapp.models import User,Course
import json
from django.core.serializers import serialize
#from .myser import UserSer,CourseSer,CategorySer
from rest_framework.response import Response
from rest_framework.views import APIView

from mydjango.settings import UPLOAD_ROOT,BASE_DIR
import os

import random
#导入绘图库
from PIL import ImageDraw
#导入绘图字体库
from PIL import ImageFont
#导入图片库
from PIL import Image
#导入io库
import io
import time

from django.shortcuts import render,HttpResponse #引入HttpResponse
from dwebsocket.decorators import accept_websocket #引入dwbsocket的accept_websocket装饰器

clients={} #创建客户端列表，存储所有在线客户端

# 允许接受ws请求

import uuid
@accept_websocket
def link(request):
    # 判断是不是ws请求
    if request.is_websocket():
        userid=str(uuid.uuid1())
        # 判断是否有客户端发来消息，若有则进行处理，若发来“test”表示客户端与服务器建立链接成功
        while True:
            message=request.websocket.wait()
            if not message:
                break
            else:
                print("客户端链接成功："+str(message, encoding = "utf-8"))
                #保存客户端的ws对象，以便给客户端发送消息,每个客户端分配一个唯一标识
                clients[userid]=request.websocket

def send(request):
    # 获取消息
    msg=request.GET.get("msg")
    # 获取到当前所有在线客户端，即clients
    # 遍历给所有客户端推送消息
    for client in clients:
        clients[client].send(msg.encode('utf-8'))
    return HttpResponse({"msg":"success"})




def my_de():
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):

            print(request.GET.get('key123'))

            try:
                de_token = jwt.decode(request.GET.get('key123'),'123',algorithms=['HS256'])
                print('登录了')
            except Exception as e:
                print('没登录')

            ret = {}
            ret['code'] = 400
            #return Response(ret)
            return HttpResponse(json.dumps(ret,ensure_ascii=False),content_type='application/json')

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


client_appid = 'wxfc9dd85023bb8840'
Mch_id = '1555664621'
Mch_key = 'Jiyun123456Jiyun123456Jiyun12345'


def myindex(request):
    return HttpResponse('这里是首页')

def myback(request):
    return HttpResponse('这里是回调网址')

def get_nonce_str():
    import uuid
    return str(uuid.uuid4()).replace('-', '')

def getWxPayOrdrID():
    import datetime
 
    date=datetime.datetime.now()
    #根据当前系统时间来生成商品订单号。时间精确到微秒
    payOrdrID=date.strftime("%Y%m%d%H%M%S%f")

    return payOrdrID

#生成签名的函数
def paysign(appid,body,mch_id,nonce_str,notify_url,openid,out_trade_no,spbill_create_ip,total_fee):
    ret= {
        "appid": appid,
        "body": body,
        "mch_id": mch_id,
        "nonce_str": nonce_str,
       "notify_url":notify_url,
        "openid":openid,
        "out_trade_no":out_trade_no,
        "spbill_create_ip":spbill_create_ip,
        "total_fee":total_fee,
        "trade_type": 'JSAPI'
    }
 
    #处理函数，对参数按照key=value的格式，并按照参数名ASCII字典序排序
    stringA = '&'.join(["{0}={1}".format(k, ret.get(k))for k in sorted(ret)])
    stringSignTemp = '{0}&key={1}'.format(stringA,Mch_key)
    sign = hashlib.md5(stringSignTemp.encode("utf-8")).hexdigest()
    return sign.upper()


def generate_sign(param):
    '''生成签名'''
    stringA = ''
    ks = sorted(param.keys())
    print(param)
    # 参数排序
    for k in ks:
        stringA += (k + '=' + param[k] + '&')
    # 拼接商户KEY
    stringSignTemp = stringA + "key=" + Mch_key
    # md5加密,也可以用其他方式
    hash_md5 = hashlib.md5(stringSignTemp.encode('utf8'))
    sign = hash_md5.hexdigest().upper()
    return sign

#获取全部参数信息，封装成xml,传递过来的openid和客户端ip，和价格需要我们自己获取传递进来
def get_bodyData(openid,client_ip,price):
    body = 'Mytest'                    #商品描述
    notify_url = 'http://localhost:8000/back'         #填写支付成功的回调地址，微信确认支付成功会访问这个接口
    nonce_str =get_nonce_str()           #随机字符串
    out_trade_no =getWxPayOrdrID()     #商户订单号
    total_fee =str(price)              #订单价格，单位是 分

    

    #获取签名                              
    sign=paysign(client_appid,body,Mch_id,nonce_str,notify_url,openid,out_trade_no,client_ip,total_fee) 
 
    bodyData = '<xml>'
    bodyData += '<appid>' + client_appid + '</appid>'             # 小程序ID
    bodyData += '<body>' + body + '</body>'                         #商品描述
    bodyData += '<mch_id>' + Mch_id + '</mch_id>'          #商户号
    bodyData += '<nonce_str>' + nonce_str + '</nonce_str>'         #随机字符串
    bodyData += '<notify_url>' + notify_url + '</notify_url>'      #支付成功的回调地址
    bodyData += '<openid>' + openid + '</openid>'                   #用户标识
    bodyData += '<out_trade_no>' + out_trade_no + '</out_trade_no>'#商户订单号
    bodyData += '<spbill_create_ip>' + client_ip + '</spbill_create_ip>'#客户端终端IP
    bodyData += '<total_fee>' + total_fee + '</total_fee>'         #总金额 单位为分
    bodyData += '<trade_type>JSAPI</trade_type>'                   #交易类型 小程序取值如下：JSAPI
 
    bodyData += '<sign>' + sign + '</sign>'
    bodyData += '</xml>'
 
    return bodyData


#统一下单支付接口
def payOrder(request):
    import time
    #获取价格 单位是分
    price= int(request.GET.get("price",1))

    #获取客户端ip
    client_ip,port=request.get_host().split(":")

    #获取小程序openid
    #openid='of2Fa5C2BNn77OOh1hfydxK4pVJc'
    openid = request.GET.get("openid")

    #请求微信的url
    url='https://api.mch.weixin.qq.com/pay/unifiedorder'

    #拿到封装好的xml数据
    body_data=get_bodyData(openid,client_ip,price)

    #获取时间戳
    timeStamp=str(int(time.time()))

    #请求微信接口下单
    respone=requests.post(url,body_data.encode("utf-8"),headers={'Content-Type': 'application/xml'})
    print(respone.content)
    #回复数据为xml,将其转为字典
    content=xmltodict.parse(respone.content)
    print(content)

    return_code = content['xml']['return_code']

    if return_code=='SUCCESS':
        prepay_id = content['xml']['prepay_id']
        # 时间戳
        timeStamp = str(int(time.time()))
        # 5. 五个参数
        data = {
            "appId":client_appid ,
            "nonceStr": get_nonce_str(),
            "package": "prepay_id=" + prepay_id,
            "signType": 'MD5',
            "timeStamp": timeStamp,
        }
        # 6. paySign签名
        paySign = generate_sign(data)
        data["paySign"] = paySign  # 加入签名
        print(data)
        # 7. 传给前端的签名后的参数
        return JsonResponse(data,safe=False,json_dumps_params={'ensure_ascii':False})
    else:
        return HttpResponse("请求支付失败")


from django.db import connection

def dictfetchall(cursor):
    desc = cursor.description
    return [
    dict(zip([col[0] for col in desc], row)) 
    
    for row in cursor.fetchall()
    
    ]


import jwt
from django.db.models import Q,F



class MyUser(APIView):
    def get(self, request):
        id = request.GET.get('id','未收到')
        print(id)

        #print(User.objects.filter(username="你好",password='202cb962ac59075b964b07152d234b70').first())

        user = User.objects.filter(Q(username='123')).first()

        User.objects.filter(Q(username='123')).update(num=F("num")+1)

        #users = User.objects.all()
        #注instance用于接受序列化的对象，many表示是queryset对象
        #books_ser = UserSer(user,many=True)
        user = UserSer(user)
        return Response(user.data)

#@my_de()
def product_all(request):

    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META.get('HTTP_X_FORWARDED_FOR') 
    else:
        ip = request.META.get('REMOTE_ADDR')

    print(ip)

    user = User.objects.filter(Q(username='123'))
    print(user)

    encoded_jwt = jwt.encode({'uid':'11'},'123',algorithm='HS256')

    print(encoded_jwt)

    encode_str = str(encoded_jwt,'utf-8')

    print(encode_str)

    de_code = jwt.decode('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1aWQiOiIxMSJ9.8wUhXvOPt7PqtWgOaXSnTcAIDT6tf94HbTexMpyVhHs','123',algorithms=['HS256'])

    print(de_code)

    # res = User.objects.filter(username__contains='你')
    # print(res[0].username)

    cursor = connection.cursor()
    
    cursor.execute('select a.id,a.username,b.title from user a left join course b on a.id = b.uid')
    
    result = dictfetchall(cursor)

    print(result)

    md5 = hashlib.md5()
    sign_str = '123'
    sign_utf8 = str(sign_str).encode(encoding="utf-8")
    md5.update(sign_utf8)
    md5_server = md5.hexdigest()
    print(md5_server)

    return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')



class TestSer(APIView):
    def post(self, request):
        response = {'code':200,'msg':'新增成功'}
        # 使用继承了Serializers序列化类的对象，反序列化
        category = CategorySer(data=request.data)
        print(request.data)
        if category.is_valid():
            category.create(category.data)
        return Response(response)




class Clist(APIView):
    def get(self, request):

        #[10:20]
        page = int(request.GET.get("page",1))
        size = int(request.GET.get("size",1))

        data_start = (page - 1) * size
        data_end = page * size

        clist = Course.objects.all()[data_start:data_end]
        count = Course.objects.count()

        clist_ser = CourseSer(clist,many=True)
        res = {}
        res['total'] = count
        res['data'] = clist_ser.data
        return Response(res)


#定义验证码类
class Myc(View):
    #定义随机颜色方法
    def get_random_color(self):
        R = random.randrange(255)
        G = random.randrange(255)
        B = random.randrange(255)
        return (R,G,B)
    #定义随机验证码
    def get(self,request):
        #定义画布大小 宽，高
        img_size = (120,50)
        #定义画笔 颜色种类,画布，背景颜色
        image = Image.new("RGB",img_size,'white')
        #定义画笔对象 图片对象,颜色类型
        draw = ImageDraw.Draw(image,'RGB')
        #定义随机字符
        source = '0123456789asdfghjkl'
        #定义四个字符
        #定义好容器，用来接收随机字符串
        code_str = ''
        for i in range(4):
            #获取随机颜色 字体颜色
            text_color = self.get_random_color()
            #获取随机字符串
            tmp_num = random.randrange(len(source))
            #获取字符集
            random_str = source[tmp_num]
            #将随机生成的字符串添加到容器中
            code_str += random_str
            #将字符画到画布上 坐标，字符串，字符串颜色，字体
            #导入系统真实字体,字号
            #my_font = ImageFont.truetype("c:\\windows\\Fonts\\arial.ttf",20)
            draw.text((10+30*i,20),random_str,text_color)
        #使用io获取一个缓存区
        buf = io.BytesIO()
        #将图片保存到缓存区
        image.save(buf,'png')

        #将随机码存储到session中
        request.session['code'] = code_str
        print(request.session['code'])

        #第二个参数声明头部信息
        return HttpResponse(buf.getvalue(),'image/png')


#定义上传视图类
class UploadTest(View):
    #定义上传方法
    def post(self,request):
        #接收文件，以对象的形式
        img = request.FILES.get("file")
        print(request.POST.get('name','未收到参数'))
        #文件名称是name属性
        #建立文件流对象
        f = open(os.path.join(UPLOAD_ROOT,'',img.name),'wb')
        #写文件 遍历图片文件流
        for chunk in img.chunks():
            f.write(chunk)
        #关闭文件流
        f.close()
        return HttpResponse(json.dumps({'filename':img.name},ensure_ascii=False),content_type='application/json')


def tem(request):
    title = "Hello Django"
    num = 110
    li = [1, 2, 3, 4, 5]
    dic = {'name': '小明', 'age': 20}
    res = User.objects.all()

    return render(request,'index.html',locals())


def wb_url(request):
    #微博接口地址
    weibo_auth_url = "https://api.weibo.com/oauth2/authorize"
    #回调网址
    redirect_url = "http://127.0.0.1:8000/md_admin/weibo"
    #应用id
    client_id = "2636039333"
    #组合url
    auth_url = weibo_auth_url + "?client_id={client_id}&redirect_uri={re_url}".format(client_id=client_id,re_url=redirect_url)
    return HttpResponse(auth_url)


def wb_back(request):
    #获取回调的code
    code = request.GET.get('code')
    #微博认证地址
    access_token_url = "https://api.weibo.com/oauth2/access_token"
    #参数
    re_dict = requests.post(access_token_url,data={
        "client_id": '2636039333',
        "client_secret": "4e2fbdb39432c31dc5c2f90be3afa5ce",
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://127.0.0.1:8000/md_admin/weibo",
    })

    re_dict = re_dict.text
    re_dict = eval(re_dict)
    print(re_dict)
    return redirect("http://localhost:8080?sina_id="+re_dict['uid'])
    #return HttpResponse(re_dict)


#信号

# from django.core.signals import request_finished,request_started
# from django.dispatch import receiver
 
# @receiver(request_started)
# def my_callback(sender, **kwargs):
#     print(sender.request_class)
#     print('\n'.join(['%s:%s' % item for item in sender.request_class.__dict__.items()]))
#     print("请求之前")



# 支付宝初始化
app_private_key_string = os.path.join(BASE_DIR,"keys/app_private_2048.txt")
alipay_public_key_string = os.path.join(BASE_DIR,"keys/alipay_public_2048.txt")


def get_order_code():
    order_no = str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
    return order_no

from .pay import AliPay

#初始化阿里支付对象
def get_ali_object():
    app_id = "2016092600603658"  #  APPID （沙箱应用）
    # 支付完成后，跳转的地址。
    return_url = "http://localhost:8000/testpay/"
    alipay = AliPay(
        appid=app_id,
        app_notify_url=return_url,
        return_url=return_url,
        app_private_key_path=app_private_key_string,
        alipay_public_key_path=alipay_public_key_string,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥
        debug=True,  # 默认False,
    )
    return alipay


def page1(request):

    # 根据当前用户的配置，生成URL，并跳转。
    money = request.POST.get('money')

    alipay = get_ali_object()

    # 生成支付的url
    query_params = alipay.direct_pay(
        subject="test",  # 商品简单描述
        out_trade_no=get_order_code(),
        total_amount=1,  # 交易金额(单位: 元 保留俩位小数)
    )

    pay_url = "https://openapi.alipaydev.com/gateway.do?{0}".format(query_params)  # 支付宝网关地址（沙箱应用）

    return redirect(pay_url)


def alipay_return(request):
    alipay = get_ali_object()
    params = request.GET.dict()
    out_trade_no = request.GET.get("out_trade_no")
    print(out_trade_no)

    sign = params.pop('sign', None)
    status = alipay.verify(params, sign)
    print('==================开始==================')
    print('GET验证', status)
    print('==================结束==================')
    return HttpResponse('支付成功')


#构造钉钉登录url
def ding_url(request):
    appid = 'dingoaukgkwqknzjvamdqh'
    redirect_uri = 'http://localhost:8000/dingding_back/'

    return redirect('https://oapi.dingtalk.com/connect/qrconnect?appid='+appid+'&response_type=code&scope=snsapi_login&state=STATE&redirect_uri='+redirect_uri)


import time
import hmac
import base64
from hashlib import sha256
import urllib
import json

from myapp.models import User

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

    re_dict = json.loads(res.text)
    print(re_dict)

    #判断是否为第一次登录
    user = User.objects.filter(username=str(re_dict["dingding_"+'user_info']['nick'])).first()

    sina_id = ''
    user_id = ''

    if user:
        #代表曾经用过钉钉登录
        sina_id = user.username
        user_id = user.id
    else:
        #代表首次登录，入库
        user = User(username=str("dingding_"+re_dict['user_info']['nick']),password='')
        #保存入库
        user.save()
        sina_id = str(re_dict['user_info']['nick'])
        #查询用户id
        user = User.objects.filter(username=str("dingding_"+re_dict['user_info']['nick'])).first()
        user_id = user.id


    #进行跳转
    return redirect("http://localhost:8080?sina_id="+str(sina_id)+"&uid="+str(user_id))

    
    