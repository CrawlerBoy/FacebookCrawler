# -*- coding: UTF-8 -*-
from mss.settings import ERROR_DICT,COLOR
from mss.items import AccountItem, FriendsItem, LikeItem, PostItem, CommentItem
from scrapy import Selector
import re, requests, datetime
requests.packages.urllib3.disable_warnings()

class Check_Page(object):
    def _check_page_source(self, response=None):
        for ele in ERROR_DICT:
            if ele in response:
                print COLOR['red'] % "error fonud in html====>>", ele
                if ele in [u"找不到页面", "Sorry, something went wrong"]:
                    continue
                return False, ERROR_DICT.get(ele, "unknow")
        return True, "good"
    

class Parse_Page(object):
    def __init__(self):
        self.proxies = { "http": "http://127.0.0.1:8118", "https": "http://127.0.0.1:8118", }   
    def _about_parse(self, selector, facebookid=None, url=None):
        print "==getAbout=="
        # 存储简介字段
        key_dict = {}
        item = AccountItem()
        item["account_id"] = facebookid
        item["account_url"] = url
        try:
            #用户头像地址
            image_link_ele = selector.xpath('//a/img[contains(@src,"https://scontent")]/@src').extract_first(default="")
            # 账号名称
            item["account_name"] = selector.xpath('//a/img[contains(@src,"https://scontent")]/@alt').extract_first(default="")
            # 获取指定信息
            friend = selector.xpath("//div[@id='root']/div[1]/div[2]/div[2]/div[1]/a/text()")
            friends_num = 0
            if len(friend) != 0:
                friends_nums = friend.extract_first()
                friends_num = re.findall(r'\d+', friends_nums)[0]
            # 指定简介信息的key
            about_list = [
                "work",
                "education",
                "skills",
                "living",
                "contact-info",
                "basic-info",
                "nicknames",
                "relationship",
                "quote",
            ]
            # 循环获取指定标签
            for key in about_list:
                elements = selector.xpath("//div[@id='%s']/div/div[2]//table/tr" % key)
                if elements:
                    ele_dict = {}
                    for ele in elements:
                        data_key, value = tuple(ele.xpath("td").xpath("string(.)").extract())
                        if ele_dict.has_key(data_key):
                            new_value = ele_dict[data_key]
                            new_value = (new_value + [value]) if isinstance(new_value,list) else [new_value,value]
                            ele_dict[data_key]=new_value
                        else:
                            ele_dict[data_key]=value
                    key_dict[key] = ele_dict
                else:
                    key_dict[key] = selector.xpath("//div[@id='%s']/div/div[2]" % key).xpath("string(.)").extract_first(default="")
            div_ele = selector.xpath("//div[@id='family']/div/div[2]/div/div")
            family_dict = {}
            for ele in div_ele:
                ele_data = ele.xpath('h3').xpath('string(.)').extract()
                if ele_data:
                    family_dict.update(dict([tuple(ele_data)]))

            div_ele = selector.xpath("//div[@id='year-overviews']/div/div[2]/div/div")
            year_overviews = {}
            for ele in div_ele:
                overviews = ele.xpath('div/div').xpath('string(.)').extract()
                if len(overviews) > 1:
                    year,content = overviews[0],overviews[1:] 
                    year_overviews[year]=content

            item["account_friend"] = friends_num
            item["account_live"] = key_dict.get('living','')
            item["account_from"] = ''
            item["account_joined"] = ''
            item["account_like"] = ''
            item["account_follow"] = ''
            item['account_image_link'] = image_link_ele.xpath('@src').extract_first(default="")
            item['nicknames'] = key_dict.get('nicknames')
            item['family'] = family_dict
            item['skills'] = key_dict.get('skills')
            item['work'] = key_dict.get('work')
            item['education'] = key_dict.get('education')
            item['relationship'] = key_dict.get('relationship')
            item['contact_info'] = key_dict.get('contact-info')
            item['basic_info'] = key_dict.get('basic-info')
            item['quote'] = key_dict.get('quote')
            item['year_overviews'] = year_overviews

        except Exception as e:
            print COLOR['red'] % u"about link Error===>>%s" % e

        # 返回简介信息
        return item

    def _friend_parse(self, response, facebookid=None):
        try:
            print "==getFriend=="
            table_eles = response.xpath('//table')#[@role="presentation"]')
            for table_ele in table_eles: 
                image_link = table_ele.xpath('tbody/tr/td/img[contains(@src,"https://scontent") and @width="50"]/@src').extract()
                account_info = table_ele.xpath('tbody/tr/td/div/span/text()').extract()
                friends = table_ele.xpath('tbody/tr/td/a[contains(@href,"fref=fr_tab")]')
                name_link = [friend.xpath('text()').extract() + friend.xpath('@href').extract() for friend in friends]
                for name,link in name_link:
                    item = FriendsItem()
                    item["friend_from"] = facebookid
                    item["friend_to"] = link.split("&")[0] if link.split("&") else link
                    item["friend_name"] = name
                    item['friend_image_link'] = image_link[0] if image_link else ''
                    item['friend_info'] = account_info[0] if account_info else ''
                    yield item
        except Exception as e:
            print self.red % u"friend link Error===>>%s"%e
    
    def _like_parse(self, response, facebookid=None):
        try:
            print "==getLikes=="
            point_eles = response.xpath('//div[@id="objects_container"]/div/div')
            for ele in point_eles:
                image_link = ele.xpath('div/div/div/img[contains(@src,"https://scontent") and @width="50"]/@src').extract()
                likes = ele.xpath('div/div/div/div/a[1]')
                name_link = [like.xpath('span/text()').extract() + like.xpath('@href').extract() for like in likes]
                for name,link in name_link:
                    item = LikeItem()
                    item['like_from'] = facebookid
                    item['like_to'] = link.split("&")[0] if link.split("&") else link
                    item['like_name'] = name
                    item['like_image_link'] = image_link[0] if image_link else ''
                    yield item
        except Exception as e:
            print COLOR['red'] % u"like link Error===>>%s"%e

    # 解析评论
    def _get_comments_by_xpath(self, selector):
        comments = []
        xpath = ""
        # comments xpath 第一种情况
        for num in range(3, 6):
            xpath_a = "//div[@id='m_story_permalink_view']/div[2]/div/div[%s]/div" % num
            xpath_b = "//div[@id='MPhotoContent']/div[2]/div/div/div[%s]/div" % num
            if selector.xpath(xpath_a):
                xpath = xpath_a
                comments = selector.xpath(xpath_a)
            if selector.xpath(xpath_b):
                xpath = xpath_b
                comments = selector.xpath(xpath_b)
            if comments:
                break
        return comments, xpath

    # 时间转换器
    def _time_converter(self,date):
        new_date = None
        patterns = {
            re.compile(ur"(\d{1,2})小时前"): lambda d, pa=None: (
            datetime.datetime.now() - datetime.timedelta(hours=int(pa.findall(d)[0]))).strftime(
                '%Y年%m月%d日 %H:%M').decode('utf-8'),
            re.compile(ur"\d{1,2}月\d+日 \d+:\d+"): lambda d, pa=None: str(datetime.date.today())[:4] + u"年" + d,
            re.compile(ur"\d{1,2}月\d+日上午 \d+:\d+"): lambda d, pa=None: str(datetime.date.today())[:4] + u"年" +
                                                                       d.split(u"上午")[0],
            re.compile(ur"\d{1,2}月\d+日下午 \d+:\d+"): lambda d, pa=None: str(datetime.date.today())[:4] + u"年" +
                                                                       d.split(u"下午")[0],
            re.compile(ur"^\d+年\d+月\d+日"): lambda d, pa=None: d,
            re.compile(ur"^\d+年$"): lambda d, pa=None: d + u"1月1日",
            re.compile(ur"^\d+年\d+月$"): lambda d, pa=None: d + u"1日",
            re.compile(ur"^\d{1,2}月\d+日$"): lambda d, pa=None: str(datetime.date.today())[:4] + u"年" + d,
            re.compile(ur"^\d{5,6}月\d+日$"): lambda d, pa=None: d[:4] + u"年" + d[4:],
        }
        if u"昨天" in date:
            today = datetime.date.today()
            yesterday = today - datetime.timedelta(days=1)
            return yesterday.strftime('%Y年%m月%d日 %H:%M').decode('utf-8')
        for key, func in patterns.items():
            if key.findall(date):
                new_date = func(date, pa=key)
                break
        return new_date

    def _process_content(self, selector):
        content_xpath = [
            "//div[@id='m_story_permalink_view']/div[1]/div/div/div",
            "//div[@id='objects_container']/div[1]",
            "//div[@id='MPhotoContent']/div/div[2]/span/div/div",
        ]
        for xpath in content_xpath:
            xpath_objs = selector.xpath(xpath).extract()
            if xpath_objs:
                content = selector.xpath(xpath).xpath("string(.)")[1:].extract_first(default="")
                timestamp = selector.xpath(xpath + "/abbr/text()").extract_first(default="")
                # if timestamp:
                    # timestamp = self._time_converter(timestamp)
                if timestamp:
                    return content, timestamp
        return "", ""

    def _install_item(self, item_cls, kwargs):
        _item = item_cls()
        [_item.setdefault(key, kwargs.get(key, "")) for key in _item.fields]
        return _item

    def _process_title(self, selector):
        return selector.xpath("//div[@id='m_story_permalink_view']/div[1]/div/div/div/h3").xpath("string(.)").extract_first(default="")

    # 评论数据提取
    def _parse_comments(self, comments, facebook_id=None, post_id=""):
        i = 0
        print "==parse_comments=="
        _comments = []
        for comment in comments:
            if not comment:
                print "empty comment!!!"
                continue
            comment_element = "".join(comment.extract())
            if (u"see_next_" in comment_element) or (u"see_pre" in comment_element):
                continue
            comment_user_link = comment.xpath("div/h3/a/@href").extract_first()
            comment_user_name = comment.xpath("div/h3/a/text()").extract_first()
            comment_content = comment.xpath("div/div[1]").xpath("string()").extract_first()
            comment_time = comment.xpath("//div/div/div[3]/abbr/text()").extract()[i]
            i += 1
            comment_love = comment.xpath("//div/div[3]/span/span/a/text()").extract()[1] if len(comment.xpath(
                "//div/div[3]/span/span/a/text()").extract())>1 else ""
            comment_id_links = comment.xpath("//div/div/div[3]/a/@href").extract()
            comment_id = comment.root.attrib.get("id", "")
            if not comment_id:
                p = re.compile("ctoken=(\d+_\d+)")
                for link in comment_id_links:
                    if "comment/replies/?" in link:
                        result = re.findall(p, link)
                        if result:
                            comment_id = result[0].split("_")[1]
                            break
            if comment_user_link:
                comment_kwards = {}
                comment_fb_id = comment_user_link.split("&")[0]
                comment_fb_id = comment_fb_id[1:] if comment_fb_id.startswith("/") else comment_fb_id
                comment_kwards['post_id'] = post_id
                comment_kwards['author_id'] = facebook_id
                comment_kwards['comment_id'] = comment_id
                comment_kwards['comment_content'] = comment_content
                comment_kwards['comment_date'] = comment_time
                comment_kwards['comment_love'] = comment_love
                comment_kwards['comment_fb_id'] = comment_fb_id
                comment_item = self._install_item(CommentItem, comment_kwards)
                _comments.append(comment_item)
        return _comments

    # 帖子、评论解析
    def get_Post_Comment(self, PostUrl, facebookId, selector, request):
        comments_content = []
        post_item = PostItem()
        # 帖子ID
        p = re.compile("story_fbid=(\d+)|fbid=(\d+)")
        id = re.findall(p, PostUrl)
        try:
            post_id = id[0][0] if id[0][0] else id[0][1]
        except:
            post_id = ""
        # 帖子源页面
        html = selector.xpath("//div[@id='m_story_permalink_view']/div[1]").extract_first() or selector.xpath(
            "//div[@id='objects_container']/div[1]").extract_first()
        # 内容
        content, timestamp = self._process_content(selector)
        # title
        title = self._process_title(selector)
        reactions = selector.xpath("//div[@id='m_story_permalink_view']/div[2]/div/div[3]/a/@href").extract_first()

        # 抓取当前页面的comments
        comments, xpath = self._get_comments_by_xpath(selector)
        _comments = self._parse_comments(comments, facebook_id=facebookId, post_id=post_id)
        for _comment in _comments:
            comments_content.append(_comment)
        reactions_data = {}
        reaction_link = "https://m.facebook.com" + reactions if reactions else ''
        post_item['post_url'] = PostUrl
        post_item['post_id'] = post_id
        post_item['post_title'] = title
        post_item['post_content'] = content
        post_item['post_date'] = timestamp
        post_item['post_place'] = ""
        post_item['author_id'] = facebookId
        post_item['post_love'] = reactions_data.get(u"大爱", "") or reactions_data.get("Love", "")
        post_item['post_sad'] = reactions_data.get(u"心碎", "") or reactions_data.get("Sad", "")
        post_item['post_wow'] = reactions_data.get(u"哇", "") or reactions_data.get("Wow", "")
        post_item['post_like'] = reactions_data.get(u"赞", "") or reactions_data.get("Like", "")
        post_item['post_angry'] = reactions_data.get(u"怒", "") or reactions_data.get("Angry", "")
        post_item['post_haha'] = reactions_data.get(u"笑趴", "") or reactions_data.get("Haha", "")
        post_item['post_shared'] = ""
        yield post_item,comments_content,reaction_link