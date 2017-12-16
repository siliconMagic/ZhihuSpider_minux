# coding:utf-8
"""
@Function:
登录知乎网站，使用自己的知乎账号密码
爬取登录后的页面信息，信息包括话题类别，答主，话题名等信息的爬取

@author:Minux
@date:2017-12-13
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import urllib.request
import random
import os
import sys
import time
from zheye import zheye
from http import cookiejar

'''
# python2中设置字体编码为utf-8
reload(sys)
sys.setdefaultencoding('utf-8')
'''

log_dir = './zhihu_log'

class ZhiHuSpider(object):
    url = 'https://www.zhihu.com/login/email'

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def login_zhihu_web(self):
        '''
        登录页面的测试代码
        FireFox手动进行第一次登陆
        '''
        # driver = webdriver.Firefox()
        driver = webdriver.PhantomJS()
        driver.get(ZhiHuSpider.url)
        driver.maximize_window()

        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        # driver.save_screenshot(log_dir+'/login_index.png')
        # 找到index页面的登录按钮点击,使用账号密码登录
        driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/a[2]').click()
        driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[2]/span').click()
        # driver.save_screenshot(log_dir+'/login_pass.png')
        driver.find_element_by_name('account').send_keys(self.username)
        driver.find_element_by_name('password').send_keys(self.password)
        driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/form/div[2]/button').click()
        time.sleep(2)
        driver.save_screenshot(log_dir+'/login_valid_code.png')
        '''
        在login_valid_code.png中发现出现了倒立汉字的验证码，先将将验证码图片进行保存
        '''

        valid_code_src = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/form/div[1]/div[3]/div[2]/img').get_attribute('src')
        print(valid_code_src)
        ZhiHuSpider.save_valid_code(valid_code_src)


    @staticmethod
    def save_valid_code(v_src):
        '''
        request = urllib2.Request(v_src)
        code = urllib2.urlopen(request).read()
        '''
        code = urllib.request.urlopen(v_src).read()
        code_f = open(log_dir+'./code_py3.png','wb')
        code_f.write(code)
        code_f.close()


'''
测试逻辑代码
'''
def test_logic():

    '''
    zhihu_spider = ZhiHuSpider('aaaax','bbbbx')
    zhihu_spider.login_zhihu_web()

    '''
    z = zheye.zheye()
    pos = z.Recognize('')
    print(pos)

if __name__ == "__main__":
    test_logic()


