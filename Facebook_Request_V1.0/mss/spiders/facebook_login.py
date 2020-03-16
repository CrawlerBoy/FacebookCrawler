# -*- coding: UTF-8 -*-

from scrapy import Spider,Selector
from scrapy.http import Request, FormRequest
from requests import Session
from mss.settings import LOGINFO, FBACCOUNT, COLOR, ABOUT_START, FRIEND_START, LIKE_START, POST_COMMENT_START
import sys, re, redis, os
from mss.spiders.facebook_profile import Check_Page,Parse_Page
from mss.items import PostItem

reload(sys)
sys.setdefaultencoding('utf-8')

class FacebookLogin(Spider):

    name = 'FacebookLogin'
    _check_func = Check_Page()
    _parse_func = Parse_Page()
    tag = {ABOUT_START:"_about",FRIEND_START:"_friend",LIKE_START:"_like",POST_COMMENT_START:"_post"}.get(True)

    def __init__(self, *args, **kwargs):
        super(FacebookLogin, self).__init__(*args, **kwargs)
        self.home_url_time = 0
        self.rdb = redis.Redis(host='127.0.0.1',port=6379,db=0)
        self.base_url = 'https://m.facebook.com'

    def extractor(self, category):
        pub_scheme = '//div[@id="root"]/div/div/div[4]/a[contains(@href,"/profile.php?v=%s")]/@href' % category
        return pub_scheme

    def start_requests(self):
        return [Request("https://m.facebook.com/", meta = {'cookiejar': 1 }, callback=self.post_login)]

    #登录表单提交
    def post_login(self, response):
        print 'Preparing Login'
        return FormRequest.from_response(response,
                                            formdata={
                                                'email': LOGINFO['user']['name'],
                                                'pass': LOGINFO['user']['password']
                                            }, 
                                            callback=self.remember_browser,
                                            dont_filter=True)
    def remember_browser(self, response):
        if "checkpoint" in response.request.url:
            print COLOR['red'] % u"account checkpoint, fail"
            return
        response.meta["FBACCOUNT"]=FBACCOUNT
        return FormRequest.from_response(response,
                                                formdata={'name_action_selected': 'dont_save'},
                                                meta=response.meta,
                                                callback=self.parse_profile)

    def parse_profile(self, response):
        check, status = self._check_func._check_page_source(response=response.text)
        if not check:
            os.system('./stop_spider.sh')
        
        if "checkpoint" in response.url:
            os.system('./stop_spider.sh')

        # if response.meta.get("task"):
        #     task=response.meta["task"].strip()
        #     TaskId = self.rdb.get(task + self.tag)
        #     if TaskId:
        #         print COLOR['green'] % '<<========== Already Collect ==========>>'
        #     else:
        #         home_page_url = 'https://m.facebook.com/' + task
        #         yield Request(home_page_url,meta={'id':task,'url':home_page_url}, callback=self.parse_page)
        
        # fbaccount = response.meta["FBACCOUNT"]
        # if fbaccount:
        #     response.meta["task"]=fbaccount.pop()
        #     response.meta["FBACCOUNT"]=fbaccount
        #     yield Request('https://www.google.com',meta=response.meta, callback=self.parse_profile, dont_filter=True)
        for task in FBACCOUNT:
            home_page_url = 'https://m.facebook.com/' + task.strip()
            yield Request(home_page_url,meta={'id':task,'url':home_page_url}, callback=self.parse_page)            


    def parse_page(self, response):
        facebookId = response.meta['id']
        facebook_url = response.meta['url']
        check, status = self._check_func._check_page_source(response=response.text)
        if not check:
            os.system('./stop_spider.sh')
        
        if "checkpoint" in response.url:
            os.system('./stop_spider.sh')

        if "https://m.facebook.com/home.php?_rdr" == response.url or \
            "app_scoped_user_id" in response.url or "confirmemail" in response.url:
            self.home_url_time += 1
            if self.home_url_time == 3:
                self.home_url_time = 0
                print COLOR['red'] % "account seven_days, fail"
                os.system('./stop_spider.sh')


        if FRIEND_START:
            #Friend页面链接抽取
            friend_link_ele = response.xpath(self.extractor(category="friends")).extract()
            if not friend_link_ele:
                print COLOR['red'] % 'Not Friend Info......'
            if friend_link_ele:
                friend_url = self.base_url + friend_link_ele[0]
                yield Request(friend_url, meta={'id': facebookId}, callback=self.friend_more_handler)

        if LIKE_START:
            #Like页面链接抽取
            likes_link_ele = response.xpath(self.extractor(category="likes")).extract()
            if not likes_link_ele:
                print COLOR['red'] % 'Not Like Info......'
            if likes_link_ele:
                like_url = self.base_url + likes_link_ele[0]
                yield Request(like_url, meta={'id': facebookId}, callback=self.like_more_handler)

        if POST_COMMENT_START:
            #Post页面链接抽取
            post_link_ele = response.xpath(self.extractor(category=u"timeline")).extract()
            if post_link_ele:
                post_url = self.base_url + post_link_ele[0]
                yield Request(post_url, meta={'id': facebookId}, callback=self.post_page_handler)

        if ABOUT_START:
            about = self._parse_func._about_parse(selector=response, facebookid=facebookId, url=facebook_url)
            print COLOR['blue'] % about
            yield about

    #好友回调函数
    def friend_more_handler(self, response):
        facebookId = response.meta['id']
        check, status = self._check_func._check_page_source(response=response.text)
        if not check:
            os.system('./stop_spider.sh')
            return

        if "checkpoint" in response.url:
            os.system('./stop_spider.sh')

        if "https://m.facebook.com/home.php?_rdr" == response.url or \
            "app_scoped_user_id" in response.url or "confirmemail" in response.url:
            self.home_url_time += 1
            if self.home_url_time == 3:
                self.home_url_time = 0
                print COLOR['red'] % "account seven_days, fail"
                os.system('./stop_spider.sh')

        friends = self._parse_func._friend_parse(response=response, facebookid=facebookId)
        for friend in friends:
            yield friend
            print COLOR['green'] % friend
        friend_more_ele = response.xpath('//div[@id="m_more_friends"]/a/@href').extract()
        if friend_more_ele:
            new_friend_url = self.base_url + friend_more_ele[0]
            yield Request(new_friend_url, meta=response.meta, callback=self.friend_more_handler)

    #点赞回调函数
    def like_more_handler(self, response):
        facebookId = response.meta['id']
        check, status = self._check_func._check_page_source(response=response.text)
        if not check:
            os.system('./stop_spider.sh')

        if "checkpoint" in response.url:
            os.system('./stop_spider.sh')

        if "https://m.facebook.com/home.php?_rdr" == response.url or \
            "app_scoped_user_id" in response.url or "confirmemail" in response.url:
            self.home_url_time += 1
            if self.home_url_time == 3:
                self.home_url_time = 0
                print COLOR['red'] % "account seven_days, fail"
                os.system('./stop_spider.sh')

        likes = self._parse_func._like_parse(response=response, facebookid=facebookId)
        for like in likes:
            yield like
            print COLOR['yellow'] % like
        like_more_ele = response.xpath('//div[@id="m_more_item"]/a/@href').extract()
        if like_more_ele:
            new_like_url = self.base_url + like_more_ele[0]
            yield Request(new_like_url, meta=response.meta, callback=self.like_more_handler)

    #帖子页面列表处理器        
    def post_page_handler(self, response):
        facebookId = response.meta['id']
        check, status = self._check_func._check_page_source(response=response.text)
        if not check:
            os.system('./stop_spider.sh')

        if "checkpoint" in response.url:
            os.system('./stop_spider.sh')

        post_link_list = response.xpath('//div[@role="article"]/div[2]/div[2]/a[contains \
            (@href,"footer_action_list")]/@href').extract()
        for link in post_link_list:
            post_detail_url = self.base_url + link
            yield Request(post_detail_url, meta=response.meta, callback=self.post_comment_parse)
        more_ele = response.xpath('//div[@id="structured_composer_async_container"]/div[2]/a/@href').extract()
        if more_ele:
            more_page_url = self.base_url + more_ele[0]
            yield Request(more_page_url, meta=response.meta, callback=self.post_page_handler)
        #更多之后年份获取未写

    #帖子、评论、点赞列表获取
    def post_comment_parse(self, response):
        print '~'*30
        facebookId = response.meta['id']
        post_comment = self._parse_func.get_Post_Comment(
                                                            PostUrl=response.request.url,
                                                            facebookId=facebookId,
                                                            selector=response,
                                                            request=response.request)
        for post, comments, reaction_link in post_comment:
            for comment in comments:
                yield comment
                print COLOR['green'] % comment
            if reaction_link:
                yield Request(reaction_link, meta={'post':post}, callback=self.post_reaction_parse)
            else:
                yield post
                print COLOR['green'] % post
    
    def post_reaction_parse(self, response):
        check, status = self._check_func._check_page_source(response=response.text)
        if not check:
            os.system('./stop_spider.sh')

        if "checkpoint" in response.url:
            os.system('./stop_spider.sh')

        post_item = response.meta.get('post')
        reactions_data = {}
        links = response.xpath(
            "//table[@role='presentation']/tr/td/div/div/a") or response.xpath(
            "//tbody/tr/td/div/div[1]/a")
        for e in links:
            if e.xpath("img/@alt").extract_first():
                reactions_data[e.xpath("img/@alt").extract_first(default="")] = e.xpath(
                    "span/text()").extract_first()
        post_item['post_love'] = reactions_data.get(u"大爱", "") or reactions_data.get("Love", "")
        post_item['post_sad'] = reactions_data.get(u"心碎", "") or reactions_data.get("Sad", "")
        post_item['post_wow'] = reactions_data.get(u"哇", "") or reactions_data.get("Wow", "")
        post_item['post_like'] = reactions_data.get(u"赞", "") or reactions_data.get("Like", "")
        post_item['post_angry'] = reactions_data.get(u"怒", "") or reactions_data.get("Angry", "")
        post_item['post_haha'] = reactions_data.get(u"笑趴", "") or reactions_data.get("Haha", "")
        yield post_item
        print COLOR['green'] % post_item