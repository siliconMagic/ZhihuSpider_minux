# coding:utf-8
"""
@Function:
登录知乎网站，使用自己的知乎账号密码
爬取登录后的页面信息，信息包括话题类别，答主，话题名等信息的爬取
半自动化，需要手动登录一次

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
import re
import csv
import codecs

'''
# python2中设置字体编码为utf-8
reload(sys)
sys.setdefaultencoding('utf-8')
'''

log_dir = './zhihu_log_semi'
html_dir = './zhihu_html_semi'
csv_dir = './zhihu_csv_semi'

class ZhihuSpider(object):
    url = 'https://www.zhihu.com/login/email'

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def login_zhihu_web(self):
        '''
        登录页面的测试代码
        FireFox手动进行第一次登陆
        :return: driver 进入知乎首页
        '''
        driver = webdriver.Firefox()
        driver.get(ZhihuSpider.url)
        driver.maximize_window()

        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        # 找到index页面的登录按钮点击,使用账号密码登录
        driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/a[2]').click()
        driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[2]/span').click()
        driver.find_element_by_name('account').send_keys(self.username)
        driver.find_element_by_name('password').send_keys(self.password)
        driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/form/div[2]/button').click()
        res = input("请输入验证码,OK表示完成")
        if res.lower() == 'ok':
            print("验证通过")
            driver.save_screenshot(log_dir+'/index_login.png')
        else:
            print("请检查自己的操作")
            return -1
        return driver

    @staticmethod
    def get_info_from_index(driver, times):
        """
        对知乎首页进行爬取，并将页面代码保存到本地
        :param driver:登录后返回的driver
        :param times:向下滚动的次数,每次向下滚动一屏幕
        :return: 0/-1,0表示爬取成功，-1表示爬取失败
        """
        if not os.path.exists(html_dir):
            os.mkdir(html_dir)

        '''
        进行下滑滚动，知乎进入动态加载
        '''
        for i in range(0, times):
            driver.execute_script('window.scrollBy(0, document.body.clientHeight)')
            print("rolling page...")
            time.sleep(0.5)
        print("page load finish")

        zhihu_html = driver.page_source
        with open(html_dir+'/index.html','w', encoding='utf-8') as f_ind:
            try:
                f_ind.write(zhihu_html)
            except IOError as e:
                print(e)
                return -1
        print("zhihu index page has been saved lcoally")
        driver.close()
        return 0

    @staticmethod
    def zhihu_info_extract():
        """
        从保存的本地的知乎首页中提取信息
        主要信息包括：
        话题类别，答主昵称，答主签名，话题title,赞同数量，评论数量
        :return:0/-1,0表示数据提取成功，-1表示数据提取失败
        """
        path = html_dir+'/index.html'
        index_file = open(path, 'r', encoding='utf-8')
        soup = BeautifulSoup(index_file, 'lxml')
        topic_block = soup.find_all('div',{'class':'Card TopstoryItem'})
        # print(len(topic_block)) 目前首页中包含120个话题块
        p_topic_class = re.compile(r'<div .*? id="Popover-\d{5}-\d{5}-toggle".*?>(.*?)</div>')
        p_topic_author = re.compile(r'<a .*? class="UserLink-link.*?>(.*?)</a>')
        p_topic_title = re.compile(r'<a.*?data-za-detail-view-element_name="Title".*?>(.*?)</a>')

        topic_list = []
        author_list = []
        title_list = []
        approval_list = []
        comment_list = []
        for single_topic in topic_block:
            '''
            话题分类信息
            '''
            topic_row = single_topic.find('div', {'class':'Feed-meta'})
            # print(topic_row)
            '''
            topic_class = single_topic.find('div',{'class':'Popover'}).get_text().strip()
            if topic_class != '':
                topic_list.append(topic_class)
            else:
                topic_list.append('没有分类')
            # topic_author = single_topic.find('a',{'class':'User-link'}).get_text().strip()
            '''
            res_0 = re.search(p_topic_class,str(topic_row))
            if res_0:
                # len(res_0[1]<10说明是话题分类，不然可能是答主的hyperlink
                if len(res_0[1]) < 10:
                    topic_list.append(str(res_0[1]))
                else:
                    topic_list.append('没有分类信息')
            else:
                topic_list.append('没有分类信息')
            '''
            话题答主信息
            '''
            # author_row = single_topic.find('div', {'class':'AuthorInfo-head'})
            res_1 = re.search(p_topic_author, str(single_topic))
            if res_1:
                if len(res_1[1]) < 15:
                    author_list.append(str(res_1[1]))
                else:
                    p_author_alt = re.compile(r'<img.*?alt="(.*?)".*?>')
                    res_1_1 = re.search(p_author_alt, str(res_1[1]))
                    author_list.append(str(res_1_1[1]))
            else:
                author_list.append('没有答主信息')

            '''
            话题标题信息
            '''
            res_2 = re.search(p_topic_title, str(single_topic))
            if res_2:
                title_list.append(str(res_2[1]))
            else:
                title_list.append('没有标题信息')

            '''
            点赞数信息和评论信息
            '''
            rank_info = single_topic.find('div', {'class':'ContentItem-actions'}).get_text()
            p_num = re.compile('\d+\.?\d?[K]?')
            res_3 = re.findall(p_num, rank_info)
            if len(res_3) == 2:
                appro_num = str(res_3[0])
                comm_num = str(res_3[1])
            elif len(res_3) == 1:
                appro_num = str(res_3[0])
                comm_num = "0"
            approval_list.append(appro_num)
            comment_list.append(comm_num)

        '''
        测试返回数据
        print(len(topic_list))
        print(len(author_list))
        print(len(title_list))
        print(len(approval_list))
        print(len(comment_list))
        '''
        return topic_list, author_list, title_list, approval_list, comment_list

    @staticmethod
    def data_to_csv(info):
        """
        将提取到的信息实例化到csv文件中，实例化到mysql数据库中
        :param info:包含主题类别，答主，标题，赞同和评论的tuple
        :return:
        """
        topic_list = info[0]
        author_list = info[1]
        title_list = info[2]
        approval_list = info[3]
        comment_list = info[4]
        if not os.path.exists(csv_dir):
            os.mkdir(csv_dir)
        with open(csv_dir+'/zhihu_info.csv','w', newline='') as zh_file:
            # zh_file.write(codecs.BOM_UTF8)
            writer = csv.writer(zh_file)
            writer.writerow([u'主题类别', u'答主', u'标题', u'赞同数', u'评论数'])
            for item in zip(topic_list, author_list, title_list, approval_list, comment_list):
                    writer.writerow(item)
        print('CSV file finish')

def logic_test():
    '''
    测试逻辑
    username 和 user_password填写注册的知乎账号和密码
    '''
    # zhihu_spider = ZhihuSpider('username','user_passsword')
    # driver = zhihu_spider.login_zhihu_web()
    # ZhihuSpider.get_info_from_index(driver, 20)
    info = ZhihuSpider.zhihu_info_extract()
    ZhihuSpider.data_to_csv(info)


if __name__ == '__main__':
    logic_test()