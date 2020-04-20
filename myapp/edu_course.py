from django.shortcuts import render,redirect
#导包
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
#导入类视图
from django.views import View

from myapp.models import User,Category,Course,Comment,Flows,Codes,Orders,Chapters
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

#导入序列化类
from myapp.myser import UserSer,CategorySer,CourseSer,CommentSer,FlowsSer,CodesSer,OrdersSer,ChaptersSer


#导入中间件
from django.utils.deprecation import MiddlewareMixin


#建立redis链接
#定义ip
host = 'localhost'
#建立服务连接
r = redis.Redis(host=host)





#课程点击数统计
def course_click(request):

    cid = request.GET.get('cid')

    #使用redis有序集合来记录

    r.zincrby('course-click',1,int(cid))

    res = {}
    res['code'] = 200
    res['message'] = '页面访问成功'

    return HttpResponse(json.dumps(res,ensure_ascii=False),content_type='application/json')

#获取排行榜前n位的数据
def get_top_n_users(num):

    #获取所有有序集合元素 进行切片操作
    course_clicks = r.zrevrange('course-click',0,-1,withscores=True)[:num]

    #和mysql联动
    course = Course.objects.in_bulk([int(item[0]) for item in course_clicks])

    #将点击数和mysql结果集结合
    res = []
    #遍历
    for item in course_clicks:

        try:
            res.append({int(item[1]):course[int(item[0])]})
        except Exception as e:
            print(str(e))
            pass
    return res

#获取排行榜真实数据
def get_course_list(request):

    #调用数据
    get_course = get_top_n_users(3)

    res = []

    #拼装json
    for dic in get_course:
        for k,v in dic.items():
            #序列化
            data = CourseSer(v).data
            #增加字段
            data['click_number'] = k
            res.append(data)
    
    return HttpResponse(json.dumps(res,ensure_ascii=False),content_type='application/json')






#使用装饰器来验证用户合法性
def my_de():
    def decorator(view_func):
        def _wraped_view(request,*args,**kwargs):

            #获取参数
            uid = request.GET.get('uid')
            token = request.GET.get('token')

            #解码操作
            try:
                decode_jwt = jwt.decode(token,'123',algorithms=['HS256'])
            except Exception as e:
                print(str(e))
                ret = {}
                ret['code'] = 401
                ret['message'] = '您是非法用户'
                return HttpResponse(json.dumps(ret,ensure_ascii=False),content_type='application/json')
            
            #判断是否篡改
            if str(uid) != str(decode_jwt['uid']):
                ret = {}
                ret['code'] = 401
                ret['message'] = '您篡改了用户id'
                return HttpResponse(json.dumps(ret,ensure_ascii=False),content_type='application/json')

        
            return view_func(request,*args,**kwargs)

        return _wraped_view
    return decorator




#转换器，将结果集list转换为dict
def dictfetchall(cursor):

    #创建描述对象
    desc = cursor.description

    return [

        dict(zip([col[0] for col in desc],row))

        for row in cursor.fetchall()

    ]

#我的关注接口
@my_de()
def myflows(request):

    uid = request.GET.get('uid')

    #建立游标对象
    cursor = connection.cursor()

    #执行sql语句
    cursor.execute(" select a.username,c.title from user a left join flows b on a.id = b.uid left join course c on b.cid = c.id where a.id = %s  " % str(uid))

    #获取结果集
    result = dictfetchall(cursor)

    #返回结果集
    return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')


#导入支付基类
from mydjango.pay import AliPay


#设置支付宝公钥和私钥
#私钥
app_private_key_string = os.path.join(BASE_DIR,"keys/app_private_2048.txt")
#共钥
alipay_public_key_string = os.path.join(BASE_DIR,"keys/alipay_public_2048.txt")

#初始化阿里支付对象
def get_ali_object():

    app_id = '2016092600603658'
    #回调网址
    return_url = "http://localhost:8000/ali_back/"
    #实例化对象
    alipay = AliPay(

        appid=app_id,
        app_notify_url = return_url,
        return_url = return_url,
        #私钥地址
        app_private_key_path = app_private_key_string,
        #公钥地址
        alipay_public_key_path = alipay_public_key_string,
        debug=True
    )

    return alipay

#支付网址视图
def ali_pay(request):

    price = request.GET.get('price')
    orderid = request.GET.get('orderid')
    #获取实例
    alipay = get_ali_object()
    #支付参数
    query_params = alipay.direct_pay(

        subject = "test",
        out_trade_no = orderid,
        total_amount = price
    )
    #拼接网址
    pay_url = "https://openapi.alipaydev.com/gateway.do?{0}".format(query_params)

    return redirect(pay_url)

#定义回调方法
def ali_back(request):

    #接收参数 订单号
    orderid = request.GET.get('out_trade_no')

    #修改订单状态
    orders = Orders.objects.get(orderid=orderid)
    orders.state = 1
    orders.save()

    #重定向回到订单列表页
    return redirect("http://localhost:8080/order")


#定义退款接口
def refund(request):

    #实例化对象
    alipay = get_ali_object()

    #接收参数
    orderid = request.GET.get('orderid')
    price = request.GET.get('price')

    #调用退款接口
    order_string = alipay.api_alipay_trade_refund(out_trade_no=orderid,refund_amount=price,notify_url='http://localhost:8000/ali_back/')

    #将已经退款的订单修改状态
    orders = Orders.objects.filter(orderid=orderid).first()
    # 2代表已经退款
    orders.state = 2
    orders.save()

    #return HttpResponse(order_string)
    #重定向回到订单列表页
    return redirect("http://localhost:8080/order")




#根据时间戳来创建订单id
def get_order_id():

    return str(time.strftime('%Y%m%d%H%M%S',time.localtime(time.time())))


#订单列表
class OrdersList(APIView):

    def get(self,request):

        uid = request.GET.get('uid')

        #查询订单
        orderslist = Orders.objects.filter(uid=int(uid))

        #序列化
        orderslist_ser = OrdersSer(orderslist,many=True)

        return Response(orderslist_ser.data)


#章节列表接口
class ChaptersList(APIView):

    def get(self,request):

        #获取参数
        cid = request.GET.get('cid')

        #查询数据
        chapters = Chapters.objects.filter(cid=int(cid))

        #序列化
        chapters_ser = ChaptersSer(chapters,many=True)

        #返回结果
        return Response(chapters_ser.data)


#章节录入接口
class ChaptersInsert(APIView):

    def get(self,request):

        #获取参数
        cid = request.GET.get('cid')
        content = request.GET.get('content')
        title = request.GET.get('title')
        module = request.GET.get('module')

        #去重
        chapters = Chapters.objects.filter(title=title).first()

        if chapters:
            res = {}
            res['code'] = 405
            res['message'] = '该章节已经存在'
            return Response(res)

        #入库
        chapters = Chapters(cid=int(cid),content=content,title=title,module=module,state=0)
        chapters.save()

        #返回结果
        res = {}
        res['code'] = 200
        res['message'] = '添加章节成功'
        return Response(res)


#订单入库
class OrderInsert(APIView):

    def get(self,request):

        #获取参数
        uid = request.GET.get('uid')
        price = request.GET.get('price')
        cids = request.GET.get('cids')
        sign_vue = request.GET.get('sign')

        #比对签名
        #生成md5对象
        md5 = hashlib.md5()
        #声明签名
        sign = price
        #转码
        sign_utf8 = str(sign).encode(encoding="utf-8")
        #加密
        md5.update(sign_utf8)
        #生成密文
        md5_server = md5.hexdigest()


        print(sign_vue)
        print(md5_server)

        if md5_server != sign_vue:
            res = {}
            res['code'] = 401
            res['message'] = '您篡改了价格，不予结账'
            return Response(res)

        #生成订单号
        orderid = get_order_id()

        #入库
        orders = Orders(uid=int(uid),price=int(price),orderid=orderid,cids=cids)
        orders.save()

        #返回
        res = {}
        res['code'] = 200
        res['message'] = '订单创建成功'

        return Response(res)




#优惠卷接口
class GetCodes(APIView):

    def get(self,request):

        #获取参数
        code = request.GET.get('code')

        #读取优惠卷
        codes = Codes.objects.filter(code=code).first()

        #判断优惠卷状态
        if codes.state == 0:
            res = {}
            res['code'] = 401
            res['message'] = '该优惠卷已经过期了'
            return Response(res)

        #使用优惠卷
        codes.state = 0
        codes.save()

        #序列化
        codes_ser = CodesSer(codes)

        #返回结果
        res = {}
        res['code'] = 200
        res['message'] = '已经使用优惠卷成功'
        res['data'] = codes_ser.data
        return Response(res)

#获取关注状态
class GetFlow(APIView):

    def get(self,request):

        #用户id
        uid = request.GET.get('uid')
        cid = request.GET.get('cid')

        #获取状态
        flows = Flows.objects.filter(uid=int(uid),cid=int(cid)).first()

        #判断状态
        if flows:
            state = 1
        else:
            state = 0

        #返回状态
        ret = {}
        ret['code'] = 200
        ret['state'] = state

        return Response(ret)


#关注接口
class FlowsInsert(APIView):

    def get(self,request):

        #用户id
        uid = request.GET.get('uid')
        cid = request.GET.get('cid')
        #关注动作
        myflow = request.GET.get('myflow')

        if myflow == "false":

            #取关
            Flows.objects.filter(uid=int(uid),cid=int(cid)).delete()

            #修改课程总关注数
            course = Course.objects.get(id=int(cid))
            course.flow = course.flow - 1
            course.save()

            #返回
            res = {}
            res['code'] = 200
            res['message'] = '取关成功'
            return Response(res)
        else:
            #入库
            flows = Flows(uid=int(uid),cid=int(cid))
            flows.save()

            #修改课程总关注数
            course = Course.objects.get(id=int(cid))
            course.flow = course.flow + 1
            course.save()

            #返回
            res = {}
            res['code'] = 200
            res['message'] = '关注成功'
            return Response(res)



#课程检索
class CourseSearch(APIView):

    def get(self,request):

        title = request.GET.get('title')

        #检索
        courselist = Course.objects.filter(title__contains=title)

        #序列化
        courselist_ser = CourseSer(courselist,many=True)

        #返回
        return Response(courselist_ser.data)


#反序列化入库
class CommentInsert(APIView):

    def post(self,request):

        #评论限速
        #判断是否在限速期限内
        if r.get('life') != None:
            res = {}
            res['code'] = 401
            res['message'] = '您的请求过于频繁'
            return Response(res)
        else:

            #设置访问限速期限
            r.set('life','life')
            r.expire('life',30)




        #初始化参数
        comment = CommentSer(data=request.data)

        #验证字段正确性
        if comment.is_valid():
            #保存数据
            comment.create(comment.data)

        #返回结果
        res = {}
        res['code'] = 200
        res['message'] = '留言成功'

        return Response(res)

#课程详情接口
class CourseDetail(APIView):

    def get(self,request):

        id = request.GET.get("id")

        #查询数据
        course = Course.objects.filter(id=int(id)).first()

        #序列化
        course_ser = CourseSer(course)

        #返回
        return Response(course_ser.data)


#课程列表接口
class CourseList(APIView):

    def get(self,request):

        #获取当前页
        page = request.GET.get("page",1)

        #获取每页的条数
        size = request.GET.get("size",2)

        #计算开始  当前页减一 乘以 页码
        data_start = (int(page)-1) * int(size)

        #计算结束位置   当前页 乘以 页码
        data_end = int(page) * int(size)

        #获取所有课程  利用切片分页
        courselist = Course.objects.all()[data_start:data_end]

        #返回数据总条数
        count = Course.objects.count()

        #序列化
        courselist_ser = CourseSer(courselist,many=True)

        #返回
        res = {}
        res['total'] = count
        res['datalist'] = courselist_ser.data 
        return Response(res)

#课程入库接口
class AddCourse(APIView):

    def get(self,request):

        #接收参数
        title = request.GET.get('title','')
        desc = request.GET.get('desc','')
        category = request.GET.get('category','')
        video = request.GET.get('video','')
        uid = request.GET.get('uid','')
        price = request.GET.get('price','')
        cid = request.GET.get('cid','')

        #排重操作
        course = Course.objects.filter(title=title).first()
        if course:
            res = {}
            res['code'] = 405
            res['message'] = '该课程已经存在'
            return Response(res)

        #进入入库
        course = Course(title=title,desc=desc,video=video,uid=int(uid),price=int(price),cid=int(cid))
        course.save()

        #返回结果
        res = {}
        res['code'] = 200
        res['message'] = '课程入库成功'
        return Response(res)


#redis限流
class RedisTest(APIView):

    def get(self,request):
        

        res = {}
        res['code'] = 200
        res['message'] = '访问成功'
        return Response(res)
        