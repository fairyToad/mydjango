from selenium import webdriver
from selenium.webdriver import ActionChains
import time

#建立浏览器实例
browser = webdriver.Chrome("c:/Users/liuyue/www/chromedriver.exe")

#打开网址
browser.get('http://localhost:8080/login')

#群体选择器
browser.find_elements_by_tag_name('input')[1].send_keys('liuyue')
browser.find_elements_by_tag_name('input')[2].send_keys('123')

#进行拖动操作
button = browser.find_element_by_class_name('dv_handler')
print(button)
#声明动作实例
action = ActionChains(browser)
#点击并且按住
action.click_and_hold(button).perform()
action.reset_actions()
#实际拖动像素和轨迹长度是有出入的
action.move_by_offset(271,0).perform()

#点击登录按钮
browser.find_element_by_class_name('h-btn').click()

#延迟等待
time.sleep(5)


#关闭浏览器
browser.close()