# -*- coding: utf-8 -*-

import scrapy

class AccountItem(scrapy.Item):
    account_id = scrapy.Field()  # 用户id
    account_name = scrapy.Field()  # 用户名称
    account_url = scrapy.Field()  # 用户url
    account_friend = scrapy.Field()  # 用户朋友数
    account_live = scrapy.Field()  # 用户所在地
    account_from = scrapy.Field()  # 用户来自
    account_joined = scrapy.Field()  # 加入时间
    account_like = scrapy.Field()  # 点赞数
    account_follow = scrapy.Field()  # 跟随数
    account_image_link = scrapy.Field() #用户头像链接
    nicknames = scrapy.Field() #昵称
    family = scrapy.Field() #家庭
    skills = scrapy.Field() #技能
    work = scrapy.Field() #工作
    education = scrapy.Field() #教育
    relationship = scrapy.Field() #关系
    contact_info = scrapy.Field() #关联信息
    basic_info = scrapy.Field() #基本信息
    quote = scrapy.Field()
    ispublic = scrapy.Field()  # 是否是公众账号
    picture = scrapy.Field()
    image_video_item = scrapy.Field() 
    year_overviews = scrapy.Field()

class FriendsItem(scrapy.Item):
    friend_from = scrapy.Field()
    friend_to = scrapy.Field()
    friend_name = scrapy.Field()
    friend_image_link = scrapy.Field()
    friend_info = scrapy.Field()

class LikeItem(scrapy.Item):
    like_image_link = scrapy.Field()
    like_from = scrapy.Field()
    like_to = scrapy.Field()
    like_name = scrapy.Field()

class PostItem(scrapy.Item):
    post_url = scrapy.Field()  # 链接
    post_id = scrapy.Field()  # 贴文ID
    author_id = scrapy.Field()  # 作者
    post_title = scrapy.Field()  # 标题
    post_content = scrapy.Field()  # 贴文内容
    post_date = scrapy.Field()  # 发表时间
    post_place = scrapy.Field()  # 发表地点
    post_love = scrapy.Field()  # 大爱
    post_sad = scrapy.Field()  # 伤心
    post_wow = scrapy.Field()  # 哇
    post_like = scrapy.Field()  # 喜欢
    post_angry = scrapy.Field()  # 愤怒
    post_haha = scrapy.Field()  # 哈哈
    post_shared = scrapy.Field()  # 分享数
    post_picture = scrapy.Field() #配图
    post_message_tags = scrapy.Field() #标签
    post_source =scrapy.Field()  #视频
    image_video_item=scrapy.Field()
    # collect_account = scrapy.Field()

class CommentItem(scrapy.Item):
    post_id = scrapy.Field()  # 帖子ID
    author_id = scrapy.Field()  # 作者
    comment_id = scrapy.Field()  # 评论ID
    comment_content = scrapy.Field()  # 评论内容
    comment_date = scrapy.Field()  # 发表时间
    comment_love = scrapy.Field()  # 点赞数
    comment_fb_id = scrapy.Field()  # 评论人id
    # collect_account = scrapy.Field()