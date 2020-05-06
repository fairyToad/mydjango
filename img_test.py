# #图像处理
import cv2


# 灰色滤镜,提高AI识图准确率
# #读图
# img = cv2.imread('./code.png',cv2.IMREAD_GRAYSCALE)
# # #写图
# cv2.imwrite('./code1.png',img)



# 加水印(根据print的参数调整水印位置)
from PIL import Image,ImageDraw 
#读图
im = Image.open("./snowgitlabk.jpg")
# 输出一些文件的参数
print(im.format,im.size,im.mode)
#生成画笔
draw = ImageDraw.Draw(im)
#根据size参数绘制水印
draw.text((1900,670),'1907',fill = (76,234,124,180))
# 载入内存展示,尚未保存到本地
im.show()




# #图像压缩(jpg比png格式小)
#读图
img = cv2.imread('./snowgitlabk.jpg')
#压缩  0-9
cv2.imwrite('./snowgitlabk1.png',img,[cv2.IMWRITE_PNG_COMPRESSION,9])
#jpg 0-100
cv2.imwrite('./snowgitlabk1.jpg',img,[cv2.IMWRITE_JPEG_QUALITY,10])


