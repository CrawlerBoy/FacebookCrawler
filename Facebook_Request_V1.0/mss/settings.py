# -*- coding: utf-8 -*-

# Scrapy settings for mss project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'mss'

SPIDER_MODULES = ['mss.spiders']
NEWSPIDER_MODULE = 'mss.spiders'
DOWNLOAD_DELAY = 0.25
IMAGES_STORE = 'images/'
LOG_LEVEL = 'INFO'
# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"

#代理IP
PROXIES = ''#必填，否则无法访问FB

# PROXIES = '119.28.117.139:1024'

#facebook账号、密码
LOGINFO = {
    "user":{
        "name":"",#email/phonenumber
        "password":""
    },
}

#页面异常包含场景
ERROR_DICT = {
    u"登录 Facebook 即可浏览个人主页": "cookies_error",
    u"你必须先登录": "cookies_error",
    u"安全验证码": "code_error",
    u"我们需要验证你的身份": "upload_photo",
    u"请上传一张您本人的照片": "upload_photo",
    u"你的帐户已被停用": "useless",
    u"使用手机验证你的帐户": "phone_number",
    u"你要求的页面无法显示": "seven_days",
    u"We Need You To Confirm Your Identity": "upload_photo",
    u"我们最近发现您的帐户在开展可疑活动": "upload_photo",
    u"Your account has been disabled": "useless",
    u"We Need You To Confirm Your Identity": "upload_photo",
    u"Upload A Photo Of Yourself": "upload_photo",
    u"Please enter your phone number": "phone_number",
    u"Please enter the text below": "code_error",
    u"You must log in first": "cookies_error",
    u"请验证你的身份":"checkpoint",
    u"The page you requested cannot be displayed right now":"page error"
}

#采集目标账号（测试账号默认三个）
FBACCOUNT = ["ma.wei.14","100005747462022","100001038746232"]

DOWNLOADER_MIDDLEWARES = {
    'mss.middlewares.ProxyMiddleware': 543,
    'mss.middlewares.PrintUrlMiddleware': 543,
}
COLOR = {
    "red":"\033[31;1m  %s  \033[0m",
    "blue":"\033[34;1m  %s  \033[0m",
    "green":"\033[1;32;40m  %s  \033[0m",
    "yellow":"\033[33;1m  %s  \033[0m",
}

#采集目标开关
ABOUT_START = True
FRIEND_START = False
LIKE_START = False
POST_COMMENT_START = False

ITEM_PIPELINES = {
    'mss.pipelines.FacebookPipeline': 300,
}
