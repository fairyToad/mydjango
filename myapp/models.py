from django.db import models

# 导入时间域
from django.utils import timezone


# 基类 (提高复用率)
class Base(models.Model):
    # 创建时间
    create_time = models.DateTimeField(default=timezone.now, null=True)
    class Meta:
        # 允许继承
        abstract = True

#轮播图
class Carousel(Base):
	name = models.CharField(max_length=200)
    # 点击跳转的链接
	src = models.CharField(max_length=200)
    # 图片
	img = models.CharField(max_length=200) 
	#声明表名
	class Meta:
		db_table = "carousel"

# 用户表
class User(Base):
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    # 存图片名,不存能路径,路径若是换个服务器或者域名,会出问题
    img = models.CharField(max_length=200)

    # 类别,用于权限管理 (使用整形,有助于提升性能)
    # 0普通用户 1超级管理员 2网站编辑 3新浪
    type = models.IntegerField(default=0, null=True)    
    phone = models.CharField(max_length=200)
    # 个人主页
    num = models.IntegerField(default=0, null=True)

    # 声明表名
    class Meta:
        db_table = 'user'
