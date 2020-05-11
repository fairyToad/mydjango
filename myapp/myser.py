#序列化反序列化

#导包
from rest_framework import serializers

#导入需要序列化的表
from myapp.models import *

#建立序列化类
class CarouselSer(serializers.ModelSerializer):
	class Meta:
		model = Carousel
		fields = "__all__"

class GoodsSer(serializers.ModelSerializer):
	class Meta:
		model = Goods
		fields = "__all__"

class CategorySer(serializers.ModelSerializer):
	class Meta:
		model = Category
		fields = "__all__"